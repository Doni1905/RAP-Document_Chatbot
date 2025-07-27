# 🤖 RAG Chat Assistant

A modern, fully offline Retrieval-Augmented Generation (RAG) chatbot that transforms your documents into intelligent conversations. Built with a beautiful, responsive UI and powered by open-source models and tools.

---

## 👥 Authors

- **Doneeswaran**
- **Rashmi**

---

![RAG Chat Assistant](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)

---

## ✨ Features

### 🎨 **Modern UI/UX**
- **Beautiful Intro Page**: Eye-catching landing page with feature highlights
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Theme Support**: Light and dark mode with smooth transitions
- **Enhanced Sidebar**: Professional gradient headers and organized sections
- **Real-time Status**: Live monitoring of Qdrant and Ollama services

### 📚 **Document Processing**
- **Multiple Formats**: Support for PDF, TXT, and DOCX files
- **Smart Chunking**: Intelligent document segmentation with context preservation
- **Instant Processing**: Fast document ingestion and indexing
- **Batch Upload**: Upload multiple documents simultaneously

### 🧠 **AI-Powered Chat**
- **Context-Aware**: Answers based on your uploaded documents
- **Source Citations**: Shows which documents and pages were used
- **Intelligent Retrieval**: Finds the most relevant information
- **Natural Conversations**: Human-like responses powered by Ollama LLMs

### ⚡ **Performance & Reliability**
- **Offline-First**: Works completely offline after initial setup
- **Fast Retrieval**: Optimized vector search with Qdrant
- **Memory Efficient**: Smart resource management
- **Scalable**: Handles large document collections

---

## 📸 Output Screenshots & Results

All project outputs, screenshots, and sample results are available at the following Google Drive link:

[👉 View Project Outputs on Google Drive](https://drive.google.com/drive/folders/1twm6pmxXxTxemngfj8DpL6KdcFEJHEH3)

---

## 🔗 Project Output Drive Link

All project outputs, including screenshots, sample runs, and documentation, are available at:

[Google Drive Output Folder](https://drive.google.com/your-output-link)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Doni1905/RAP-Document_Chatbot.git
cd RAP-Document_Chatbot
```

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Services
```bash
# Start Qdrant (Vector Database)
docker start qdrant_rag || docker run -d --name qdrant_rag -p 6333:6333 -v $(pwd)/docs_index:/qdrant/storage qdrant/qdrant

# Start Ollama (LLM Server)
ollama serve
ollama pull mistral  # or phi3, llama3, etc.
```

### 4. Launch the App
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser and start chatting! 🎉

---

## 💬 How to Use

### 📖 **Getting Started**
1. **Welcome Screen**: Enjoy the beautiful intro page showcasing key features
2. **Upload Documents**: Use the sidebar to upload your PDF, TXT, or DOCX files
3. **Process Documents**: Click "Process Documents" to index your files
4. **Start Chatting**: Ask questions about your documents in the chat interface

### 🎛️ **Sidebar Controls**
- **🎨 Theme Toggle**: Switch between light and dark modes
- **📁 Document Upload**: Drag and drop or browse for files
- **🔧 System Status**: Monitor Qdrant and Ollama services
- **🗑️ Clear Chat**: Reset conversation history
- **💡 Tips**: Helpful guidance for better results

### 💡 **Pro Tips**
- **Upload Multiple Documents**: Combine related files for better context
- **Ask Specific Questions**: Detailed questions get better answers
- **Use Natural Language**: Chat as you would with a human assistant
- **Check Sources**: Review which documents were used for answers

---

## 🏗️ Technical Architecture

### **Frontend**
- **Streamlit**: Modern, responsive web interface
- **Custom CSS**: Beautiful gradients and animations
- **Theme System**: Dynamic light/dark mode switching
- **Real-time Updates**: Live status monitoring

### **Backend**
- **Document Processing**: Intelligent chunking and embedding
- **Vector Search**: Fast similarity search with Qdrant
- **LLM Integration**: Flexible model support via Ollama
- **Session Management**: Persistent chat history

### **Data Flow**
```
Documents → Chunking → Embedding → Vector Store → Query → Retrieval → LLM → Response
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **UI Framework** | Streamlit | Web interface and user experience |
| **Vector Database** | Qdrant | Fast similarity search and storage |
| **LLM Server** | Ollama | Local model serving and inference |
| **Embedding Model** | BGE-Small-EN | Document and query vectorization |
| **Document Processing** | PyPDF, python-docx | PDF and DOCX file parsing |
| **Chunking** | Custom Algorithm | Intelligent document segmentation |

---

## 📁 Project Structure

```
RAG-Chat-Assistant/
├── 📄 app.py                 # Main Streamlit application
├── ⚙️ config.py              # Configuration settings
├── 📋 requirements.txt       # Python dependencies
├── 🚀 setup.sh               # Automated setup script
├── 📚 ingest/                # Document processing
│   ├── document_loader.py    # File loading utilities
│   └── chunker.py           # Text chunking algorithm
├── 🔍 retrieval/             # Vector search
│   ├── embedder.py          # Embedding generation
│   └── vectorstore.py       # Qdrant integration
├── 🧠 generation/            # LLM integration
│   └── llm_wrapper.py       # Ollama communication
├── 🛠️ utils/                 # Utilities
│   ├── logger.py            # Logging system
│   └── timer.py             # Performance monitoring
├── 📁 data/                  # User documents
├── 📊 docs_index/            # Vector database storage
├── 🤖 models/                # Local model files
└── 📖 README.md              # This documentation
```

---

## 🎯 Use Cases

### 📚 **Academic Research**
- Analyze research papers and academic documents
- Extract key insights from large document collections
- Generate summaries and answer specific questions

### 💼 **Business Intelligence**
- Process company reports and documentation
- Extract insights from business documents
- Answer questions about organizational knowledge

### 📖 **Personal Knowledge Management**
- Organize and query personal documents
- Create a searchable knowledge base
- Get instant answers from your document library

### 🎓 **Educational Support**
- Study assistance from course materials
- Quick reference for textbooks and notes
- Interactive learning from educational content

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Optional: Set custom ports
export QDRANT_PORT=6333
export OLLAMA_PORT=11434
export STREAMLIT_PORT=8501
```

### **Model Selection**
```bash
# Pull different models for Ollama
ollama pull mistral      # Fast, good quality
ollama pull phi3         # Lightweight, efficient
ollama pull llama3       # High quality, larger
ollama pull codellama    # Code-focused responses
```

---

## 🚀 Performance Tips

### **Optimization**
- **RAM**: 16GB+ recommended for smooth operation
- **Storage**: SSD preferred for faster document processing
- **CPU**: Multi-core processor for parallel processing
- **GPU**: Optional for faster embedding generation

### **Scaling**
- **Large Documents**: Process in batches for better performance
- **Multiple Users**: Consider separate instances for heavy usage
- **Document Updates**: Re-process documents when they change

---

## 🐛 Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| **Qdrant not accessible** | Check Docker is running: `docker ps` |
| **Ollama connection failed** | Verify Ollama is running: `ollama list` |
| **Document upload fails** | Check file format (PDF, TXT, DOCX only) |
| **Slow responses** | Consider using a faster model or more RAM |
| **Theme not switching** | Refresh the browser page |

### **Logs & Debugging**
```bash
# Check Streamlit logs
streamlit run app.py --logger.level debug

# Monitor Qdrant
docker logs qdrant_rag

# Check Ollama status
ollama list
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
isort .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qdrant Team** for the excellent vector database
- **Ollama Community** for making local LLMs accessible
- **Streamlit Team** for the amazing web framework
- **Hugging Face** for the BGE embedding models
- **Open Source Community** for all the amazing tools

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Doni1905/RAP-Document_Chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Doni1905/RAP-Document_Chatbot/discussions)
- **Documentation**: [Wiki](https://github.com/Doni1905/RAP-Document_Chatbot/wiki)

---

**Made with ❤️ using open-source tools**
