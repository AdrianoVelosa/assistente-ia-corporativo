# tests.py
# Testes unitários para o Assistente IA Corporativo

import unittest
import os
import tempfile
import json
from app import app
from utils import sanitize_input, format_prompt, process_model_response

class AssistenteIATestCase(unittest.TestCase):
    """Testes unitários para o Assistente IA Corporativo"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Configurar a aplicação para testes
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-key'
        
        # Criar cliente de teste
        self.client = app.test_client()
        
        # Configurar sessão de teste
        with self.client.session_transaction() as sess:
            sess['username'] = 'testuser'
            sess['role'] = 'user'
    
    def test_index_route(self):
        """Testar rota principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Assistente IA Corporativo', response.data)
    
    def test_login_route(self):
        """Testar rota de login"""
        # Limpar sessão
        with self.client.session_transaction() as sess:
            sess.clear()
        
        # Testar GET
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
        # Testar POST com credenciais inválidas
        response = self.client.post('/login', data={
            'username': 'invalid',
            'password': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_ask_route(self):
        """Testar rota de perguntas"""
        # Testar sem autenticação
        with self.client.session_transaction() as sess:
            sess.clear()
        
        response = self.client.post('/ask', json={
            'question': 'Teste'
        })
        self.assertEqual(response.status_code, 401)
        
        # Testar com autenticação
        with self.client.session_transaction() as sess:
            sess['username'] = 'testuser'
            sess['role'] = 'user'
        
        # Simular resposta do modelo (em um teste real, mockamos a função run_llama_model)
        app.config['TESTING_MODEL_RESPONSE'] = "Esta é uma resposta de teste."
        
        response = self.client.post('/ask', json={
            'question': 'Teste'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('timestamp', data)
    
    def test_sanitize_input(self):
        """Testar função de sanitização de entrada"""
        # Testar remoção de caracteres perigosos
        self.assertEqual(sanitize_input("hello; rm -rf /"), "hello rm -rf /")
        
        # Testar limite de tamanho
        long_input = "a" * 2000
        self.assertEqual(len(sanitize_input(long_input)), 1000)
        
        # Testar entrada vazia
        self.assertEqual(sanitize_input(""), "")
        self.assertEqual(sanitize_input(None), "")
    
    def test_format_prompt(self):
        """Testar formatação de prompt"""
        question = "Como funciona o modelo LLaMA?"
        prompt = format_prompt(question)
        
        # Verificar se o prompt contém a pergunta
        self.assertIn(question, prompt)
        
        # Verificar se o prompt está no formato correto
        self.assertIn("[INST]", prompt)
        self.assertIn("[/INST]", prompt)
        
        # Testar com prompt de sistema personalizado
        system_prompt = "Você é um assistente técnico."
        prompt = format_prompt(question, system_prompt)
        self.assertIn(system_prompt, prompt)
    
    def test_process_model_response(self):
        """Testar processamento de resposta do modelo"""
        # Testar remoção de prompt
        response = "[INST] Pergunta [/INST]\nResposta do modelo"
        processed = process_model_response(response)
        self.assertEqual(processed, "Resposta do modelo")
        
        # Testar remoção de tokens
        response = "<s>Resposta do modelo</s>"
        processed = process_model_response(response)
        self.assertEqual(processed, "Resposta do modelo")
        
        # Testar resposta vazia
        self.assertIn("Desculpe", process_model_response(""))

if __name__ == '__main__':
    unittest.main()