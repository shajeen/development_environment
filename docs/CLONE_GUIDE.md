# 📋 Environment Cloning Guide

## How to Clone Environments

### 1. Select Source Environment
- Choose any environment from the Docker or Vagrant sections
- Click the **"📋 Clone"** button

### 2. Clone Dialog Fields

#### **Unique Identifier**
- **Purpose**: Internal system name for your environment
- **Format**: Short, lowercase, no spaces
- **Examples**: 
  - `my-python-dev`
  - `cpp-project-1`
  - `cuda-ml-env`
- **Usage**: Used for folder names, container names, and system identification

#### **Display Name**
- **Purpose**: Human-readable name shown in the GUI
- **Format**: Any descriptive text
- **Examples**:
  - `My Python Development`
  - `C++ Project #1`
  - `CUDA ML Environment`

#### **SSH Port**
- **Purpose**: Port number for SSH access
- **Auto-suggested**: Next available port
- **Range**: 1000-65535
- **Must be unique**: No two environments can share the same port

### 3. Clone Process
1. Fill in the **Unique Identifier** (e.g., `my-custom-env`)
2. Modify the **Display Name** if needed
3. Confirm the **SSH Port** (auto-suggested)
4. Click **"✅ Clone Environment"** or press Enter
5. Wait for success confirmation
6. New environment appears in the appropriate section

### 4. What Gets Cloned
- **Configuration**: All environment settings
- **Directory Structure**: Copies source environment files
- **Docker/Vagrant Files**: Updates with new names and ports
- **Unique Settings**: New container names, image names, ports

### 5. Tips
- Use descriptive but short unique identifiers
- Keep names consistent with your project structure
- Remember the SSH port for accessing your environment
- Test the cloned environment before making changes

## Example Clone Flow

**Source**: `docker-python` → **Clone**: `my-ml-project`

- **Unique Identifier**: `my-ml-project`
- **Display Name**: `My ML Project Environment`
- **SSH Port**: `5001`

**Result**: New environment accessible via `ssh dev@localhost -p 5001`