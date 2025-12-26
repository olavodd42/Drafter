# Drafter AI Agent

Drafter é um assistente de escrita inteligente construído com LangGraph e LangChain. Ele ajuda a criar, atualizar e salvar documentos de texto através de uma interface de conversação ou via comandos de voz.

## Funcionalidades

- **Edição de Documentos**: Atualiza o conteúdo do documento com base em instruções em linguagem natural.
- **Interface Web**: Interface amigável construída com Streamlit.
- **Suporte a Áudio**: Transcreve e executa comandos de voz usando OpenAI Whisper.
- **Persistência**: Salva o documento final em um arquivo `.txt`.
- **Memória de Estado**: Mantém o contexto das alterações durante a sessão.

## Pré-requisitos

- Python 3.9+
- Chave de API da OpenAI
- FFmpeg (necessário para o Whisper processar áudio)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/olavodd42/Drafter.git
cd Drafter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
pip install streamlit openai-whisper
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto e adicione sua chave da OpenAI:
```
OPENAI_API_KEY=sk-...
```

## Como usar

### Interface Web (Recomendado)
Para usar a interface gráfica com suporte a upload e gravação de áudio:
```bash
streamlit run app.py
```

### Interface de Linha de Comando (CLI)
Para usar via terminal:
```bash
python Drafter.py
```

## Estrutura do Projeto

- `app.py`: Interface frontend construída com Streamlit.
- `Drafter.py`: Lógica do agente (backend) com LangGraph e ferramentas.
- `requirements.txt`: Lista de dependências do projeto.
