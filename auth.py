import json
import streamlit as st
from pathlib import Path

AUTH_FILE = Path(__file__).parent / "auth_config.json"


def carregar_config_auth():
    """Carrega o arquivo de configuração de autenticação."""
    if not AUTH_FILE.exists():
        st.error(f"Arquivo de configuração não encontrado: {AUTH_FILE}")
        st.stop()
    
    with open(AUTH_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def verificar_credenciais(email, senha):
    """Verifica se o email e senha estão corretos."""
    config = carregar_config_auth()
    
    for user in config.get("users", []):
        if user["email"] == email and user["password"] == senha:
            return True, user
    
    return False, None


def obter_email_contato():
    """Retorna o email de contato para requisitar acesso."""
    config = carregar_config_auth()
    return config.get("contact_email", "suporte@example.com")


def login():
    """Exibe a tela de login e retorna True se autenticado."""
    # Se já está autenticado na sessão, retorna True
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True
    
    # Exibir tela de login
    st.set_page_config(page_title="Login - Relatório de Agentes", layout="centered")
    st.title("🔐 Relatório de Agentes - TMA")
    st.markdown("---")
    st.subheader("Faça login para continuar")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="seu.email@dbm.com.br")
        senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
        submit = st.form_submit_button("Entrar", use_container_width=True)
    
    if submit:
        if not email or not senha:
            st.error("❌ Por favor, preencha email e senha.")
            return False
        
        autenticado, user = verificar_credenciais(email, senha)
        
        if autenticado:
            # Salvar na sessão
            st.session_state.authenticated = True
            st.session_state.user = user
            st.success(f"✅ Bem-vindo, {user['name']}!")
            st.rerun()
        else:
            st.error("❌ Email ou senha incorretos.")
            
            # Exibir mensagem de contato
            email_contato = obter_email_contato()
            st.warning(
                f"📧 Se você não tem acesso, entre em contato com o suporte:\n\n"
                f"**Email:** {email_contato}\n\n"
                f"**Informações a incluir no email:**\n"
                f"- Seu nome completo\n"
                f"- Seu email corporativo\n"
                f"- Seu cargo/departamento"
            )
    
    return False


def logout():
    """Faz logout do usuário."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


def obter_usuario_atual():
    """Retorna o usuário atualmente autenticado."""
    return st.session_state.get("user", None)


def requer_autenticacao(func):
    """Decorator para proteger funções que requerem autenticação."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated", False):
            login()
            return
        return func(*args, **kwargs)
    return wrapper
