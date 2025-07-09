# Troubleshooting Guide

## Common Issues and Solutions

### ❌ Environment path not found

**Problem:** GUI shows "Environment path not found: /path/to/environment"

**Cause:** The environment configuration points to a non-existent directory path.

**Solution:**
1. **Check current configurations:**



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

