# Drafter AI Agent

Drafter é um assistente de escrita inteligente construído com LangGraph e LangChain. Ele ajuda a criar, atualizar e salvar documentos de texto através de uma interface de conversação.

## Funcionalidades

- **Edição de Documentos**: Atualiza o conteúdo do documento com base em instruções em linguagem natural.
- **Persistência**: Salva o documento final em um arquivo `.txt`.
- **Memória de Estado**: Mantém o contexto das alterações durante a sessão.

## Pré-requisitos

- Python 3.9+
- Chave de API da OpenAI

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/drafter.git
cd drafter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto e adicione sua chave da OpenAI:
```
OPENAI_API_KEY=sk-...
```

## Como usar

Execute o script principal:

```bash
python Drafter.py
```

Siga as instruções no terminal para interagir com o agente.

## Estrutura do Projeto

- `Drafter.py`: Código principal contendo a lógica do agente e definição do grafo.
- `requirements.txt`: Lista de dependências do projeto.
