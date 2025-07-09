#!/bin/bash
# Setup script for DevEnvOps

echo "🐳 Setting up DevEnvOps"
echo "=" * 50

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "⚙️ Making scripts executable..."
chmod +x docker_manager.py
chmod +x setup.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Usage:"
echo "  Console: source venv/bin/activate && python docker_manager.py list"
echo "  GUI:     source venv/bin/activate && python docker_manager_gui.py"
echo ""
echo "📚 Documentation: README.md"
