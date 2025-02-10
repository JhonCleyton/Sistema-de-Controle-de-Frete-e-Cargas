# Sistema de Controle de Cargas

<div align="center">
    <img src="static/logo1.png" alt="Logo" width="200">
</div>

## 📋 Sobre o Projeto

O Sistema de Controle de Cargas é uma solução completa para gerenciamento logístico, desenvolvida para otimizar e controlar operações de transporte de cargas. Este sistema oferece uma interface intuitiva e recursos avançados para gestão eficiente de frota, motoristas e cargas.

### 🌟 Principais Funcionalidades

- **Gestão de Cargas**
  - Cadastro e acompanhamento de cargas
  - Controle de status em tempo real
  - Histórico completo de movimentações

- **Controle de Frota**
  - Gerenciamento de veículos
  - Manutenções preventivas e corretivas
  - Controle de combustível

- **Gestão de Motoristas**
  - Cadastro completo de motoristas
  - Controle de documentação
  - Gestão de folgas e escalas

- **Relatórios e Analytics**
  - Dashboards interativos
  - Relatórios personalizados
  - Indicadores de desempenho (KPIs)

## 🚀 Tecnologias Utilizadas

- **Backend**
  - Python 3.8+
  - Flask Framework
  - SQLAlchemy ORM
  - Flask-Login para autenticação
  - Flask-WTF para formulários seguros

- **Frontend**
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - jQuery
  - Font Awesome e Boxicons

- **Banco de Dados**
  - SQLite (desenvolvimento)
  - Suporte para PostgreSQL (produção)

## 💻 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno
- Git (opcional, para versionamento)

## 🔧 Instalação

1. Clone o repositório
```bash
git clone https://github.com/JhonCleyton/controle-cargas.git
cd controle-cargas
```

2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicialize o banco de dados
```bash
flask db upgrade
flask init-db
```

6. Execute o sistema
```bash
flask run
```

## 📱 Recursos Móveis

O sistema é totalmente responsivo e pode ser acessado através de dispositivos móveis, oferecendo:

- Interface adaptativa
- Acesso rápido a funcionalidades principais
- Notificações em tempo real
- PWA (Progressive Web App) support

## 🔒 Segurança

- Autenticação segura de usuários
- Proteção contra CSRF
- Senhas criptografadas
- Controle de acesso baseado em papéis (RBAC)
- Sessões seguras

## 📈 Roadmap

- [ ] Integração com APIs de rastreamento
- [ ] App mobile nativo
- [ ] Módulo de BI avançado
- [ ] Integração com sistemas SAP
- [ ] Suporte a múltiplas filiais

## 👥 Contribuição

Contribuições são sempre bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Contato e Suporte

- **Desenvolvedor**: Jhon Cleyton
- **Empresa**: JC Byte - Soluções em tecnologia
- **Email**: tecnologiajcbyte@gmail.com
- **GitHub**: [/JhonCleyton](https://github.com/JhonCleyton)
- **LinkedIn**: [/jhon-freire](https://linkedin.com/in/jhon-freire)
- **WhatsApp**: [73 99854-7885](https://wa.me/5573998547885)

---

<div align="center">
    <p>Desenvolvido por Jhon Cleyton</p>
    <p>JC Byte - Soluções em tecnologia</p>
    <p>© 2025 Todos os direitos reservados</p>
</div>
