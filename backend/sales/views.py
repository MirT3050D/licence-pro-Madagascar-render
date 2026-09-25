from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
from django.db.models.functions import TruncDate
from .models import MethodePaiement, Vente, Commande, MediaBuyerCommission
from .serializers import MethodePaiementSerializer, VenteSerializer, VenteCreateSerializer, MediaBuyerCommissionSerializer
from accounts.models import Utilisateur
from clients.models import Provenance


class MethodePaiementViewSet(viewsets.ModelViewSet):
    queryset = MethodePaiement.objects.all().prefetch_related('ventes')
    serializer_class = MethodePaiementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search') or self.request.query_params.get('q')
        status_param = self.request.query_params.get('status')

        if search:
            search = search.strip()
            qs = qs.filter(Q(label__icontains=search) | Q(details__icontains=search))

        if status_param == 'active':
            qs = qs.filter(is_active=True)
        elif status_param == 'inactive':
            qs = qs.filter(is_active=False)

        return qs.order_by('-is_active', 'label')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ventes_count = instance.ventes.count()
        if ventes_count > 0:
            return Response(
                {
                    'error': f"Impossible de supprimer « {instance.label} » car elle est rattachée à {ventes_count} vente(s). Vous pouvez la désactiver à la place."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])
        return Response(self.get_serializer(instance).data)


class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all().select_related(
        'client', 'client__provenance', 'user_affilie', 'user_affilie__role', 'methode_paiement'
    ).prefetch_related(
        'commandes__produit__activations'
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VenteCreateSerializer
        return VenteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtres
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')
        user_id = self.request.query_params.get('vendeur') or self.request.query_params.get('user_affilie')
        methode_id = self.request.query_params.get('methode_paiement')
        client_id = self.request.query_params.get('client')
        provenance_id = self.request.query_params.get('provenance')
        search = self.request.query_params.get('search') or self.request.query_params.get('q')

        if date_debut:
            qs = qs.filter(date__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(date__date__lte=date_fin)
        if user_id:
            qs = qs.filter(user_affilie_id=user_id)
        if methode_id:
            qs = qs.filter(methode_paiement_id=methode_id)
        if client_id:
            qs = qs.filter(client_id=client_id)
        if provenance_id:
            qs = qs.filter(client__provenance_id=provenance_id)
        if search:
            search = search.strip()
            qs = qs.filter(
                Q(client__nom__icontains=search) |
                Q(client__numero__icontains=search) |
                Q(client__provenance__label__icontains=search) |
                Q(id__icontains=search)
            )

        return qs.order_by('-date')

    def create(self, request, *args, **kwargs):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur (niveau 50) peut enregistrer de nouvelles ventes."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vente = serializer.save()
        read_serializer = VenteSerializer(vente)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur (niveau 50) peut modifier des ventes."},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vente = serializer.save()
        read_serializer = VenteSerializer(vente)
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur (niveau 50) peut supprimer des ventes."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtres Dashboard
        vendeur_id = request.query_params.get('vendeur') or request.query_params.get('user_affilie')
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        methode_id = request.query_params.get('methode_paiement')
        client_id = request.query_params.get('client')
        provenance_id = request.query_params.get('provenance')

        ventes_qs = Vente.objects.all().prefetch_related('commandes__produit')
        commandes_qs = Commande.objects.select_related('produit', 'vente')

        if vendeur_id:
            ventes_qs = ventes_qs.filter(user_affilie_id=vendeur_id)
            commandes_qs = commandes_qs.filter(vente__user_affilie_id=vendeur_id)
        if date_debut:
            ventes_qs = ventes_qs.filter(date__date__gte=date_debut)
            commandes_qs = commandes_qs.filter(vente__date__date__gte=date_debut)
        if date_fin:
            ventes_qs = ventes_qs.filter(date__date__lte=date_fin)
            commandes_qs = commandes_qs.filter(vente__date__date__lte=date_fin)
        if methode_id:
            ventes_qs = ventes_qs.filter(methode_paiement_id=methode_id)
            commandes_qs = commandes_qs.filter(vente__methode_paiement_id=methode_id)
        if client_id:
            ventes_qs = ventes_qs.filter(client_id=client_id)
            commandes_qs = commandes_qs.filter(vente__client_id=client_id)
        if provenance_id:
            ventes_qs = ventes_qs.filter(client__provenance_id=provenance_id)
            commandes_qs = commandes_qs.filter(vente__client__provenance_id=provenance_id)

        # 1. Total KPI
        total_ventes = ventes_qs.count()

        ca_total = 0.0
        marge_nette = 0.0
        quantite_totale = 0

        for cmd in commandes_qs:
            st = float(cmd.quantite * cmd.prix_unitaire)
            cout = float(cmd.quantite * cmd.produit.prix_achat)
            ca_total += st
            marge_nette += (st - cout)
            quantite_totale += cmd.quantite

        # 2. Évolution des ventes par jour
        evolution_ventes = (
            ventes_qs.annotate(jour=TruncDate('date'))
            .values('jour')
            .annotate(nb_ventes=Count('id'))
            .order_by('jour')
        )

        # 3. Répartition par méthode de paiement
        repartition_paiements = (
            ventes_qs.values('methode_paiement__label')
            .annotate(nb_ventes=Count('id'))
            .order_by('-nb_ventes')
        )

        # 4. Top 5 produits les plus vendus
        top_produits = (
            commandes_qs.values('produit__id', 'produit__nom')
            .annotate(
                total_quantite=Sum('quantite'),
                total_ca=Sum(F('quantite') * F('prix_unitaire'), output_field=DecimalField())
            )
            .order_by('-total_quantite')[:5]
        )

        # 5. Classement des vendeurs
        vendeurs_qs = Utilisateur.objects.select_related('role').filter(is_active=True)
        if vendeur_id:
            vendeurs_qs = vendeurs_qs.filter(id=vendeur_id)

        classement_vendeurs = []
        for v in vendeurs_qs:
            user_ventes = v.ventes.all()
            if date_debut:
                user_ventes = user_ventes.filter(date__date__gte=date_debut)
            if date_fin:
                user_ventes = user_ventes.filter(date__date__lte=date_fin)
            if methode_id:
                user_ventes = user_ventes.filter(methode_paiement_id=methode_id)
            if client_id:
                user_ventes = user_ventes.filter(client_id=client_id)
            if provenance_id:
                user_ventes = user_ventes.filter(client__provenance_id=provenance_id)

            nb_v = user_ventes.count()
            ca_v = sum(vente.total for vente in user_ventes)
            pts = v.role.point if v.role else 0
            classement_vendeurs.append({
                'id': v.id,
                'nom_complet': f"{v.prenom} {v.nom}",
                'email': v.email,
                'role': v.role.label if v.role else 'Sans rôle',
                'points': pts,
                'nombre_ventes': nb_v,
                'chiffre_affaires': ca_v
            })

        classement_vendeurs.sort(key=lambda x: (x['chiffre_affaires'], x['points'], x['nombre_ventes']), reverse=True)

        # 6. Commission Media Buyer
        mb_config = MediaBuyerCommission.objects.filter(is_active=True).first()
        if not mb_config:
            mb_config = MediaBuyerCommission.objects.create(
                cout_pub=Decimal('0.00'),
                regle_ca=Decimal('10.00'),
                regle_benefice=Decimal('30.00'),
                seuil_marge=Decimal('40.00'),
                base_recouvrement='benefice'
            )
            fb_wa = Provenance.objects.filter(label__iregex=r'(facebook|whatsapp)')
            if fb_wa.exists():
                mb_config.provenances.set(fb_wa)

        eligible_prov_ids = list(mb_config.provenances.values_list('id', flat=True))

        if provenance_id:
            try:
                p_id_int = int(provenance_id)
                if p_id_int in eligible_prov_ids:
                    mb_commandes = commandes_qs.filter(vente__client__provenance_id=p_id_int)
                else:
                    mb_commandes = Commande.objects.none()
            except (ValueError, TypeError):
                mb_commandes = Commande.objects.none()
        else:
            mb_commandes = commandes_qs.filter(vente__client__provenance_id__in=eligible_prov_ids)
        mb_commandes = mb_commandes.order_by('date', 'id')

        ca_eligible = 0.0
        benefice_eligible = 0.0
        nb_articles_eligible = 0

        # Commissions effectives (uniquement sur ce qui dépasse le coût pub)
        comm_regle_ca = 0.0
        comm_regle_benefice = 0.0
        ca_marge_haute_commissionnee = 0.0
        benefice_marge_basse_commissionnee = 0.0

        # Commission brute théorique (ce qui aurait été généré sans déduction de pub)
        commission_brute_totale = 0.0

        seuil_marge_val = float(mb_config.seuil_marge)
        pct_ca = float(mb_config.regle_ca) / 100.0
        pct_benefice = float(mb_config.regle_benefice) / 100.0
        cout_pub_val = float(mb_config.cout_pub)

        # Suivi de l'amortissement chronologique du coût publicitaire
        cumul_recouvrement = 0.0

        for cmd in mb_commandes:
            ca_l = float(cmd.quantite * cmd.prix_unitaire)
            cout_l = float(cmd.quantite * cmd.produit.prix_achat)
            benef_l = ca_l - cout_l

            ca_eligible += ca_l
            benefice_eligible += benef_l
            nb_articles_eligible += cmd.quantite

            taux_marge = (benef_l / ca_l * 100.0) if ca_l > 0 else 0.0
            is_haute_marge = (taux_marge > seuil_marge_val)

            # Calcul brut théorique
            if is_haute_marge:
                c_brut = ca_l * pct_ca
            else:
                c_brut = max(0.0, benef_l) * pct_benefice
            commission_brute_totale += c_brut

            # Montant de cette ligne servant à amortir le coût pub
            val_recouvrement = benef_l if mb_config.base_recouvrement == 'benefice' else ca_l

            if cout_pub_val <= 0:
                # Pas de coût pub -> 100% de la ligne est commissionnable
                ratio_surplus = 1.0
            else:
                cumul_avant = cumul_recouvrement
                cumul_apres = cumul_avant + max(0.0, val_recouvrement)
                cumul_recouvrement = cumul_apres

                if cumul_apres <= cout_pub_val:
                    # Intégralement dans la tranche d'amortissement de la pub
                    ratio_surplus = 0.0
                elif cumul_avant >= cout_pub_val:
                    # Entièrement au-delà du seuil de pub
                    ratio_surplus = 1.0
                else:
                    # Ligne charnière qui franchit le seuil
                    surplus = cumul_apres - cout_pub_val
                    ratio_surplus = (surplus / val_recouvrement) if val_recouvrement > 0 else 0.0
                    ratio_surplus = max(0.0, min(1.0, ratio_surplus))

            # Application de la commission sur la portion excédentaire (surplus)
            if ratio_surplus > 0:
                if is_haute_marge:
                    base_ca_part = ca_l * ratio_surplus
                    c = base_ca_part * pct_ca
                    comm_regle_ca += c
                    ca_marge_haute_commissionnee += base_ca_part
                else:
                    base_benef_part = max(0.0, benef_l) * ratio_surplus
                    c = base_benef_part * pct_benefice
                    comm_regle_benefice += c
                    benefice_marge_basse_commissionnee += base_benef_part

        commission_due = comm_regle_ca + comm_regle_benefice
        recouvrement_actuel = benefice_eligible if mb_config.base_recouvrement == 'benefice' else ca_eligible

        if cout_pub_val <= 0:
            seuil_atteint = True
            progression_recouvrement = 100.0
            reste_a_recouvrir = 0.0
        else:
            seuil_atteint = recouvrement_actuel >= cout_pub_val
            progression_recouvrement = min(100.0, round((recouvrement_actuel / cout_pub_val) * 100.0, 1))
            reste_a_recouvrir = max(0.0, cout_pub_val - recouvrement_actuel)

        commission_media_buyer = {
            'config': {
                'id': mb_config.id,
                'cout_pub': cout_pub_val,
                'regle_ca': float(mb_config.regle_ca),
                'regle_benefice': float(mb_config.regle_benefice),
                'seuil_marge': seuil_marge_val,
                'base_recouvrement': mb_config.base_recouvrement,
                'provenances': list(mb_config.provenances.values('id', 'label')),
            },
            'statut': {
                'seuil_atteint': seuil_atteint,
                'cout_pub': cout_pub_val,
                'recouvrement_actuel': round(recouvrement_actuel, 2),
                'reste_a_recouvrir': round(reste_a_recouvrir, 2),
                'progression_recouvrement': progression_recouvrement,
                'base_recouvrement_label': "Bénéfice brut" if mb_config.base_recouvrement == 'benefice' else "Chiffre d'affaires",
            },
            'commission_due': round(commission_due, 2),
            'commission_brute_theorique': round(commission_brute_totale, 2),
            'ca_eligible': round(ca_eligible, 2),
            'benefice_eligible': round(benefice_eligible, 2),
            'nb_articles_eligible': nb_articles_eligible,
            'details': {
                'marge_haute': {
                    'description': f"> {seuil_marge_val}% marge",
                    'base_ca': round(ca_marge_haute_commissionnee, 2),
                    'taux': float(mb_config.regle_ca),
                    'commission': round(comm_regle_ca, 2),
                },
                'marge_basse': {
                    'description': f"<= {seuil_marge_val}% marge",
                    'base_benefice': round(benefice_marge_basse_commissionnee, 2),
                    'taux': float(mb_config.regle_benefice),
                    'commission': round(comm_regle_benefice, 2),
                }
            }
        }

        return Response({
            'kpis': {
                'chiffre_affaires': ca_total,
                'marge_nette': marge_nette,
                'nombre_ventes': total_ventes,
                'quantite_totale': quantite_totale,
                'commission_media_buyer': round(commission_due, 2),
            },
            'chiffre_affaires': ca_total,
            'marge_nette': marge_nette,
            'nombre_ventes': total_ventes,
            'quantite_totale': quantite_totale,
            'commission_media_buyer': commission_media_buyer,
            'evolution_ventes': list(evolution_ventes),
            'repartition_paiements': list(repartition_paiements),
            'top_produits': list(top_produits),
            'classement_vendeurs': classement_vendeurs,
        })


class MediaBuyerCommissionConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        config = MediaBuyerCommission.objects.filter(is_active=True).first()
        if not config:
            config = MediaBuyerCommission.objects.create(
                cout_pub=Decimal('0.00'),
                regle_ca=Decimal('10.00'),
                regle_benefice=Decimal('30.00'),
                seuil_marge=Decimal('40.00'),
                base_recouvrement='benefice',
                is_active=True
            )
            fb_wa = Provenance.objects.filter(label__iregex=r'(facebook|whatsapp)')
            if fb_wa.exists():
                config.provenances.set(fb_wa)
        return config

    def get(self, request):
        config = self.get_object()
        serializer = MediaBuyerCommissionSerializer(config)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        is_admin = (
            user.is_staff or 
            user.is_superuser or 
            (user.role and user.role.point >= 50) or 
            (user.role and user.role.nom == 'admin')
        )
        if not is_admin:
            return Response(
                {"error": "Permission refusée. Seul un administrateur peut modifier la configuration de commission."},
                status=status.HTTP_403_FORBIDDEN
            )
        config = self.get_object()
        serializer = MediaBuyerCommissionSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)
