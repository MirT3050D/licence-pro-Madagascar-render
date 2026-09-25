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

        # Vérifier si une clé d'API LLM (Gemini ou OpenAI) est disponible
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')

        parsed_data = None

        if gemini_api_key:
            parsed_data = self._call_gemini(texte, produits_catalogue, methodes_paiement, gemini_api_key)
        elif openai_api_key:
            parsed_data = self._call_openai(texte, produits_catalogue, methodes_paiement, openai_api_key)
        
        # Fallback intelligent local si aucune clé d'API ou si échec de l'appel
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
            if p_nom in lower_txt:
                qty = 1
                qty_match = re.search(r'(\d+)\s*(?:x\s*)?' + re.escape(p_nom), lower_txt)
                if qty_match:
                    qty = int(qty_match.group(1))

                articles_trouves.append({
                    'produit_id': prod['id'],
                    'produit_nom': prod['nom'],
                    'quantite': qty,
                    'prix_unitaire': prod['prix_actif']
                })

        methode_trouvee_id = None
        for meth in methodes:
            if meth['label'].lower() in lower_txt:
                methode_trouvee_id = meth['id']
                break

        nom_client = ""
        nom_match = re.search(r"(?:je\s+suis|m'appelle|client\s*:?|de\s+la\s+part\s+de)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)", lower_txt, re.IGNORECASE)
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
