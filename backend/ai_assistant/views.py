import os
import json
import re
import urllib.request
import urllib.error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from catalog.models import Produit
from clients.models import Client
from sales.models import MethodePaiement


def get_vertex_gemini_model(model_name="gemini-2.5-flash"):
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        from google.oauth2 import service_account

        # 1. Vérifier si la clé de compte de service est injectée en variable d'environnement (ex: Render)
        sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if sa_json:
            try:
                info = json.loads(sa_json)
                credentials = service_account.Credentials.from_service_account_info(info)
                project = info.get("project_id", os.getenv("VERTEXAI_PROJECT", "jhpiego-504511"))
                vertexai.init(project=project, location=os.getenv("VERTEXAI_LOCATION", "us-central1"), credentials=credentials)
                return GenerativeModel(model_name)
            except Exception as e_sa:
                print(f"[Vertex AI SA Env Warning]: {e_sa}")

        # 2. Vérifier si un fichier local gcp-key.json existe
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_key_path = os.path.join(base_dir, "gcp-key.json")
        if os.path.exists(local_key_path):
            try:
                with open(local_key_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(info)
                project = info.get("project_id", "jhpiego-504511")
                vertexai.init(project=project, location=os.getenv("VERTEXAI_LOCATION", "us-central1"), credentials=credentials)
                return GenerativeModel(model_name)
            except Exception as e_file:
                print(f"[Vertex AI File Warning]: {e_file}")

        # 3. Fallback ADC standard (gcloud local)
        project = os.getenv("VERTEXAI_PROJECT", "jhpiego-504511")
        vertexai.init(project=project, location=os.getenv("VERTEXAI_LOCATION", "us-central1"))
        return GenerativeModel(model_name)
    except Exception as e:
        print(f"[Vertex AI Init Warning]: {e}")
        return None


class AIParsingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        texte = request.data.get('texte', '').strip()
        if not texte:
            return Response({'error': 'Le texte à analyser est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        # Contexte de la base de données
        produits = list(Produit.objects.all().prefetch_related('prix_set'))
        produits_catalogue = [
            {
                'id': p.id,
                'nom': p.nom,
                'prix_actif': float(p.prix_actif or 0)
            }
            for p in produits
        ]
        methodes_paiement = [
            {'id': m.id, 'label': m.label}
            for m in MethodePaiement.objects.filter(is_active=True)
        ]

        parsed_data = None

        # 1. Vertex AI en priorité (authentification gcloud ADC locale)
        parsed_data = self._call_vertex_parsing(texte, produits_catalogue, methodes_paiement)

        # 2. Clé Gemini ou OpenAI si Vertex AI indisponible
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')

        if not parsed_data and gemini_api_key:
            parsed_data = self._call_gemini(texte, produits_catalogue, methodes_paiement, gemini_api_key)
        elif not parsed_data and openai_api_key:
            parsed_data = self._call_openai(texte, produits_catalogue, methodes_paiement, openai_api_key)
        
        # 3. Fallback intelligent local si aucune API disponible
        if not parsed_data:
            parsed_data = self._fallback_rule_based_parser(texte, produits_catalogue, methodes_paiement)

        # Vérifier si le client existe déjà dans la base
        if parsed_data.get('client_nom'):
            client_existant = Client.objects.filter(nom__icontains=parsed_data['client_nom']).first()
            if client_existant:
                parsed_data['client_id'] = client_existant.id
                if not parsed_data.get('client_numero') and client_existant.numero:
                    parsed_data['client_numero'] = client_existant.numero

        return Response(parsed_data)

    def _call_vertex_parsing(self, texte, catalogue, methodes):
        try:
            model = get_vertex_gemini_model("gemini-2.5-flash")
            if not model:
                return None

            system_prompt = (
                "Tu es l'assistant IA intelligent de 'Licence Pro Madagascar'. "
                "Ton rôle est d'analyser les messages bruts de clients (en français, malgache ou argot local) "
                "et d'extraire les données nécessaires pour pré-remplir un bon de commande de licences logicielles.\n\n"
                "Tu dois impérativement faire correspondre les produits demandés avec le catalogue fourni ci-dessous. "
                "Si un produit demandé ressemble à un produit du catalogue (ex: 'win 11' -> 'Windows 11 Pro', 'office' -> 'Microsoft Office 365'), "
                "sélectionne l'ID et le nom du catalogue.\n\n"
                f"CATALOGUE DISPONIBLE:\n{json.dumps(catalogue, ensure_ascii=False, indent=2)}\n\n"
                f"MÉTHODES DE PAIEMENT DISPONIBLES:\n{json.dumps(methodes, ensure_ascii=False, indent=2)}\n\n"
                "Format attendu STRICTEMENT en JSON:\n"
                "{\n"
                "  \"client_nom\": string,\n"
                "  \"client_numero\": string,\n"
                "  \"methode_paiement_id\": number ou null,\n"
                "  \"articles\": [\n"
                "    {\n"
                "      \"produit_id\": number,\n"
                "      \"produit_nom\": string,\n"
                "      \"quantite\": number,\n"
                "      \"prix_unitaire\": number\n"
                "    }\n"
                "  ],\n"
                "  \"notes\": string\n"
                "}"
            )

            prompt = f"{system_prompt}\n\nMESSAGE DU CLIENT À ANALYSER:\n\"\"\"\n{texte}\n\"\"\""
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[Vertex AI Parsing Info]: {e}")
            return None

    def _call_gemini(self, texte, catalogue, methodes, api_key):
        """Appel officiel à l'API Google Gemini avec extraction JSON structurée"""
        models_to_try = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']

        system_prompt = (
            "Tu es l'assistant IA intelligent de 'Licence Pro Madagascar'. "
            "Ton rôle est d'analyser les messages bruts de clients (en français, malgache ou argot local) "
            "et d'extraire les données nécessaires pour pré-remplir un bon de commande de licences logicielles.\n\n"
            "Tu dois impérativement faire correspondre les produits demandés avec le catalogue fourni ci-dessous. "
            "Si un produit demandé ressemble à un produit du catalogue (ex: 'win 11' -> 'Windows 11 Pro', 'office' -> 'Microsoft Office 365'), "
            "sélectionne l'ID et le nom du catalogue.\n\n"
            f"CATALOGUE DISPONIBLE:\n{json.dumps(catalogue, ensure_ascii=False, indent=2)}\n\n"
            f"MÉTHODES DE PAIEMENT DISPONIBLES:\n{json.dumps(methodes, ensure_ascii=False, indent=2)}\n\n"
            "Format attendu STRICTEMENT en JSON:\n"
            "{\n"
            "  \"client_nom\": string,\n"
            "  \"client_numero\": string,\n"
            "  \"methode_paiement_id\": number ou null,\n"
            "  \"articles\": [\n"
            "    {\n"
            "      \"produit_id\": number,\n"
            "      \"produit_nom\": string,\n"
            "      \"quantite\": number,\n"
            "      \"prix_unitaire\": number\n"
            "    }\n"
            "  ],\n"
            "  \"notes\": string\n"
            "}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nMESSAGE DU CLIENT À ANALYSER:\n\"\"\"\n{texte}\n\"\"\""}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        data_bytes = json.dumps(payload).encode('utf-8')

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key.strip()}"
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    res_body = response.read().decode('utf-8')
                    result_json = json.loads(res_body)
                    parts = result_json.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        extracted = json.loads(parts[0]['text'])
                        extracted['parser'] = f'gemini ({model_name})'
                        return extracted
            except urllib.error.HTTPError as e:
                err_text = e.read().decode('utf-8', errors='ignore')
                print(f"[Gemini API Error {e.code} with {model_name}]: {err_text}")
                continue
            except Exception as e:
                print(f"[Gemini Exception with {model_name}]: {str(e)}")
                continue

        return None

    def _fallback_rule_based_parser(self, texte, catalogue, methodes):
        """Parser heuristique basé sur des règles et regex si l'API LLM n'est pas disponible"""
        lower_txt = texte.lower()

        phone_match = re.search(r'(?:03[23489]|261\s?3[23489])[\s.-]?(?:\d{2}[\s.-]?){3}\d{1,2}|\b\d{8,10}\b', texte)
        numero = phone_match.group(0).replace(' ', '').replace('.', '').replace('-', '') if phone_match else ''

        articles_trouves = []
        for prod in catalogue:
            p_nom = prod['nom'].lower()
            # Direct match ou match par mots-clés essentiels (ex: 'windows 11', 'office 365', 'canva', 'kaspersky')
            keywords = [w for w in p_nom.split() if len(w) > 2 and w not in ['pro', 'plus', 'total', 'security', 'microsoft']]
            is_matched = p_nom in lower_txt or (keywords and all(k in lower_txt for k in keywords))

            if is_matched:
                qty = 1
                matched_key = p_nom if p_nom in lower_txt else (keywords[0] if keywords else p_nom)
                qty_match = re.search(r'(\d+)\s*(?:x\s*)?' + re.escape(matched_key), lower_txt)
                if not qty_match:
                    qty_match = re.search(r'(\d+)\s*(?:licences?|cl[eé]s?|comptes?)', lower_txt)
                if qty_match:
                    qty = int(qty_match.group(1))

                articles_trouves.append({
                    'produit_id': prod['id'],
                    'produit_nom': prod['nom'],
                    'quantite': qty,
                    'prix_unitaire': prod.get('prix_actif') or prod.get('prix_vente') or 0
                })

        methode_trouvee_id = None
        for meth in methodes:
            if meth['label'].lower() in lower_txt:
                methode_trouvee_id = meth['id']
                break

        nom_client = ""
        nom_match = re.search(r"(?:je\s+suis|m'appelle|client\s*:?|de\s+la\s+part\s+de|pour\s+(?:le\s+client\s+)?)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)", lower_txt, re.IGNORECASE)
        if nom_match:
            nom_client = nom_match.group(1).title()

        return {
            'client_nom': nom_client,
            'client_numero': numero,
            'client_id': None,
            'articles': articles_trouves,
            'methode_paiement_id': methode_trouvee_id,
            'parser': 'heuristique (local)'
        }

    def _call_openai(self, texte, catalogue, methodes, api_key):
        return None


class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])

        if not message:
            return Response({'error': 'Le message est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Préparation du contexte catalogue & paiements
        produits = list(Produit.objects.all().prefetch_related('prix_set', 'activations'))
        catalogue_info = []
        for p in produits:
            guide = p.activations.first().description_activation if p.activations.exists() else 'Non spécifié'
            catalogue_info.append({
                'id': p.id,
                'nom': p.nom,
                'prix_vente': float(p.prix_actif or 0),
                'prix_achat': float(p.prix_achat or 0),
                'description': p.description or '',
                'guide_activation': guide,
                'image': p.image or None
            })

        methodes = [
            {'id': m.id, 'label': m.label, 'details': m.details or ''}
            for m in MethodePaiement.objects.filter(is_active=True)
        ]

        user = request.user
        role_nom = user.role.nom if user.role else 'vendeur'
        role_label = user.role.label if user.role else 'Vendeur'
        point = user.role.point if user.role else 10

        # 1. Appel Vertex AI en priorité (authentification gcloud ADC locale)
        chat_response = self._call_vertex_chat(message, history, catalogue_info, methodes, user, role_label, point)

        # 2. Appel Gemini API directe si Vertex AI échoue et clé dispo
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not chat_response and gemini_api_key:
            chat_response = self._call_gemini_chat(message, history, catalogue_info, methodes, user, role_label, point, gemini_api_key)

        # 3. Fallback conversationnel local si APIs indisponibles
        if not chat_response:
            chat_response = self._fallback_chat(message, catalogue_info, methodes)

        # 4. Vérifier si un client correspondant à un order_intent éventuel existe
        if chat_response.get('order_intent') and chat_response['order_intent'].get('client_nom'):
            c_nom = chat_response['order_intent']['client_nom']
            client_existant = Client.objects.filter(nom__icontains=c_nom).first()
            if client_existant:
                chat_response['order_intent']['client_id'] = client_existant.id
                if not chat_response['order_intent'].get('client_numero') and client_existant.numero:
                    chat_response['order_intent']['client_numero'] = client_existant.numero

        return Response(chat_response)

    def _call_vertex_chat(self, message, history, catalogue, methodes, user, role_label, point):
        try:
            model = get_vertex_gemini_model("gemini-2.5-flash")
            if not model:
                return None

            system_instruction = (
                "Tu es l'assistant IA officiel, intelligent, chaleureux et polyvalent de 'Licence Pro Madagascar'. "
                "Tu dialogues avec les membres de l'équipe (Administrateurs et Media Buyers/Vendeurs).\n\n"
                f"UTILISATEUR ACTUEL: {user.prenom} {user.nom} ({role_label}, Niveau de permission: {point} pts).\n\n"
                "TES MISSIONS ET CAPACITÉS:\n"
                "1. Répondre courtoisement, avec pédagogie et précision à TOUTES questions, y compris générales : techniques de vente, arguments commerciaux, objection prix, marketing digital (Facebook, TikTok, WhatsApp), informatique générale, dépannage (erreurs Windows/Office), différences entre versions logicielles et culture générale.\n"
                "2. Fournir des informations précises sur le catalogue de licences réelles ci-dessous (tarifs en Ariary, fonctionnalités, guides d'installation et d'activation).\n"
                "3. Renseigner sur les coordonnées et modalités de paiement acceptées (MVola, Orange Money, Espèces, etc.).\n"
                "4. Si l'utilisateur colle un message de commande client ou demande de préparer une vente, formule une réponse claire et génère impérativement un objet 'order_intent' contenant les détails de la commande.\n\n"
                f"CATALOGUE ACTUEL DES PRODUITS:\n{json.dumps(catalogue, ensure_ascii=False, indent=2)}\n\n"
                f"MÉTHODES DE PAIEMENT ACCEPTEES:\n{json.dumps(methodes, ensure_ascii=False, indent=2)}\n\n"
                "RÉPONSE ATTENDUE EN FORMAT JSON STRICT:\n"
                "{\n"
                "  \"reply\": \"Texte de ta réponse conversationnelle en Markdown (formaté avec puces, gras, etc.)\",\n"
                "  \"order_intent\": null ou {\n"
                "      \"client_nom\": string,\n"
                "      \"client_numero\": string,\n"
                "      \"methode_paiement_id\": number ou null,\n"
                "      \"articles\": [\n"
                "        {\n"
                "          \"produit_id\": number,\n"
                "          \"produit_nom\": string,\n"
                "          \"quantite\": number,\n"
                "          \"prix_unitaire\": number\n"
                "        }\n"
                "      ]\n"
                "   }\n"
                "}"
            )

            history_text = ""
            for h in history[-6:]:
                speaker = "Utilisateur" if h.get('role') == 'user' else "Assistant"
                history_text += f"{speaker}: {h.get('text', '')}\n"

            prompt = f"{system_instruction}\n\nHISTORIQUE RÉCENT:\n{history_text}\nNOUVEAU MESSAGE DE L'UTILISATEUR:\n{message}"

            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0.4}
            )
            data = json.loads(response.text)
            if 'reply' in data:
                return data
        except Exception as e:
            print(f"[Vertex AI Chat Info]: {e}")
            return None

    def _call_gemini_chat(self, message, history, catalogue, methodes, user, role_label, point, api_key):
        system_instruction = (
            "Tu es l'assistant IA intelligent et chaleureux de la plateforme 'Licence Pro Madagascar'. "
            "Tu dialogues avec les membres de l'équipe (Administrateurs et Media Buyers/Vendeurs).\n\n"
            f"UTILISATEUR ACTUEL: {user.prenom} {user.nom} ({role_label}, Niveau de permission: {point} pts).\n\n"
            "TES MISSIONS:\n"
            "1. Répondre courtoisement et avec précision à toute question sur les licences logicielles (Windows, Office, Antivirus, Canva, etc.), leurs tarifs en Ariary (Ar), leurs fonctionnalités et leurs guides d'installation/activation.\n"
            "2. Conseiller l'équipe sur les techniques de vente, réponses aux objections clients (ex: 'Est-ce une licence authentique ?', 'Combien de temps dure la licence ?', 'Comment payer par MVola ?').\n"
            "3. Résoudre les problèmes techniques fréquents (ex: erreur 0xC004C008, clé bloquée, réinstallation).\n"
            "4. Si l'utilisateur colle un message de commande client ou demande de préparer une vente, formule une réponse claire et génère impérativement un objet 'order_intent' contenant les détails de la commande.\n\n"
            f"CATALOGUE ACTUEL DES PRODUITS:\n{json.dumps(catalogue, ensure_ascii=False, indent=2)}\n\n"
            f"MÉTHODES DE PAIEMENT ACCEPTEES:\n{json.dumps(methodes, ensure_ascii=False, indent=2)}\n\n"
            "RÉPONSE ATTENDUE EN FORMAT JSON STRICT:\n"
            "{\n"
            "  \"reply\": \"Texte de ta réponse conversationnelle en Markdown (formaté avec puces, gras, etc.)\",\n"
            "  \"order_intent\": null ou {\n"
            "      \"client_nom\": string,\n"
            "      \"client_numero\": string,\n"
            "      \"methode_paiement_id\": number ou null,\n"
            "      \"articles\": [\n"
            "        {\n"
            "          \"produit_id\": number,\n"
            "          \"produit_nom\": string,\n"
            "          \"quantite\": number,\n"
            "          \"prix_unitaire\": number\n"
            "        }\n"
            "      ]\n"
            "   }\n"
            "}"
        )

        models_to_try = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-3.8-flash', 'gemini-1.5-flash', 'gemini-pro-latest']

        # Construction de l'historique de conversation
        contents = []
        for h in history[-8:]:  # Garder les 8 derniers échanges
            role = 'user' if h.get('role') == 'user' else 'model'
            contents.append({
                "role": role,
                "parts": [{"text": h.get('text', '')}]
            })

        # Message actuel avec instruction système
        prompt_with_context = f"{system_instruction}\n\nNOUVEAU MESSAGE:\n{message}"
        contents.append({
            "role": "user",
            "parts": [{"text": prompt_with_context}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.4
            }
        }

        data_bytes = json.dumps(payload).encode('utf-8')

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key.strip()}"
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    res_body = response.read().decode('utf-8')
                    result_json = json.loads(res_body)
                    parts = result_json.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        extracted = json.loads(parts[0]['text'])
                        if 'reply' in extracted:
                            return extracted
            except Exception as e:
                print(f"[Gemini Chat Error with {model_name}]: {e}")
                continue

        return None

    def _fallback_chat(self, message, catalogue, methodes):
        lower = message.lower()

        # 1. Détection de commande en priorité si des articles sont identifiés
        parser = AIParsingView()
        parsed = parser._fallback_rule_based_parser(message, catalogue, methodes)
        if parsed.get('articles'):
            articles_summary = ", ".join([f"{a['quantite']}x {a['produit_nom']}" for a in parsed['articles']])
            client_mention = f" pour le client **{parsed['client_nom']}**" if parsed.get('client_nom') else ""
            reply = (
                f"J'ai bien détecté une commande : **{articles_summary}**{client_mention}.\n\n"
                "Souhaitez-vous pré-remplir le formulaire de vente avec ces informations ?"
            )
            return {
                "reply": reply,
                "order_intent": parsed
            }

        # 2. Recherche de correspondances catalogue
        matches = [p for p in catalogue if p['nom'].lower() in lower]

        if "prix" in lower or "tarif" in lower or "combien" in lower:
            if matches:
                lines = [f"• **{p['nom']}** : **{p['prix_vente']:,.0f} Ar**".replace(',', ' ') for p in matches]
                reply = "Voici les tarifs pour les produits demandés :\n\n" + "\n".join(lines)
            else:
                lines = [f"• **{p['nom']}** : {p['prix_vente']:,.0f} Ar".replace(',', ' ') for p in catalogue[:6]]
                reply = "Voici un aperçu de nos principaux tarifs actuels :\n\n" + "\n".join(lines)
            return {"reply": reply, "order_intent": None}

        if "activation" in lower or "activer" in lower or "guide" in lower:
            if matches:
                p = matches[0]
                reply = f"### Procédure d'activation pour **{p['nom']}** :\n\n{p['guide_activation']}"
            else:
                reply = "Veuillez préciser le nom du produit (ex: *Windows 11 Pro*, *Office 365*) pour obtenir son guide d'activation complet."
            return {"reply": reply, "order_intent": None}

        if "paiement" in lower or "mvola" in lower or "orange" in lower or "airtel" in lower:
            lines = []
            for m in methodes:
                det = f" ({m['details']})" if m.get('details') else ""
                lines.append(f"• **{m['label']}**{det}")
            reply = "Nous acceptons les méthodes de règlement suivantes à Madagascar :\n\n" + "\n".join(lines)
            return {"reply": reply, "order_intent": None}

        return {
            "reply": (
                "Bonjour ! Je suis votre assistant virtuel **Licence Pro Madagascar**.\n\n"
                "Je peux vous renseigner sur :\n"
                "• **Les prix et disponibilités** des licences du catalogue\n"
                "• **Les guides d'activation et résolution d'erreurs** (Windows, Office, etc.)\n"
                "• **L'analyse de messages clients** pour pré-remplir une vente\n"
                "• **Les modalités de paiement** (MVola, Orange Money, Airtel, etc.)\n\n"
                "Comment puis-je vous aider aujourd'hui ?"
            ),
            "order_intent": None
        }
