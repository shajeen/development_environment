# Troubleshooting Guide

## Common Issues and Solutions

### ❌ Environment path not found

**Problem:** GUI shows "Environment path not found: /path/to/environment"

**Cause:** The environment configuration points to a non-existent directory path.

**Solution:**
1. **Check current configurations:**
   ```bash
   source venv/bin/activate
   python docker_manager.py list
   ```

2. **Fix the path using edit command:**
   ```bash
   python docker_manager.py edit <env_key> --field path --value <correct_path>
   ```

3. **Example fix:**
   ```bash
   # If cpp environment points to wrong path
   python docker_manager.py edit cpp --field path --value "docker/cpp"
   ```

4. **Verify available paths:**
   ```bash
   ls docker/  # Lists available Docker environments
   ls workspaces/  # Lists available workspace templates
   ```

### ✅ Prevention Features Added

1. **Enhanced Error Messages:** Shows available paths and fix commands
2. **Path Validation:** Warns when editing paths that don't exist
3. **Port Conflict Detection:** Prevents duplicate port assignments
4. **GUI Validation:** Edit dialogs validate paths and ports before saving

### 🔧 Validation Commands

```bash
# Test all configurations
python test_gui.py

# List all environments and their status
python docker_manager.py list

# Check specific environment info
python docker_manager.py info <env_key>

# List all editable fields
python docker_manager.py fields
```

### 🐳 Docker Issues

**Problem:** Permission denied connecting to Docker daemon

**Solution:**
1. **Start Docker daemon:**
   ```bash
   sudo systemctl start docker
   ```

2. **Add user to docker group:**
   ```bash
   sudo usermod -aG docker $USER
   # Then logout and login again
   ```

3. **Test Docker access:**
   ```bash
   docker ps
   ```

### 🚀 Quick Recovery

If configurations get corrupted:

1. **Backup current config:**
   ```bash
   cp docker_environments.json docker_environments.json.backup
   ```

2. **Reset to defaults:**
   ```bash
   rm docker_environments.json
   python docker_manager.py list  # Recreates defaults
   ```

3. **Or manually fix the JSON file:**
   ```json
   {
     "cpp": {
       "name": "C++ Development",
       "path": "docker/cpp",
       "port": 3001,
       "container": "cpp.workspace.common",
       "image": "cpp.workspace.image",
       "volume": "cpp.workspace.common.volume"
     }
   }
   ```

### 📋 Environment Structure

Correct directory structure:
```
development_environment/
├── docker/
│   ├── cpp/            # C++ environment
│   ├── cuda/           # CUDA environment
│   ├── python/         # Python environment
│   └── my_cpp/         # Cloned environments
├── workspaces/
│   └── python.cuda.template/
└── docker_environments.json
```

### 🛠️ Maintenance Commands

```bash
# Update environment name
python docker_manager.py edit cpp --field name --value "My C++ Environment"

# Update environment port
python docker_manager.py edit cpp --field port --value 3005

# Interactive editing
python docker_manager.py interactive-edit cpp

# Clone environment
python docker_manager.py clone my_env --source cpp --new-name "My Environment"
```