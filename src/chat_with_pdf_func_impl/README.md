
Example request:

curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"pdf_url": "https://arxiv.org/pdf/1810.04805.pdf", "question": "what is the name of the new language representation model introduced in the document", "chat_history":[] }' \
     http://localhost:7071/api/chatwithpdfinvoke
