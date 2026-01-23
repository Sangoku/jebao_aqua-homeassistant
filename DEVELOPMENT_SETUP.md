# Local Development Setup with Docker

This guide will help you set up a Docker-based Home Assistant environment for developing and testing the Jebao Aqua integration.

## Prerequisites

```bash
# Required
- Docker Desktop installed
- Git
- Text editor (VS Code recommended)

# Verify installations
docker --version
git --version
```

## Step 1: Create Development Directory Structure

```bash
# Create project directory
mkdir -p ~/ha-dev/jebao-dev
cd ~/ha-dev/jebao-dev

# Clone the integration repository
git clone https://github.com/chrisc123/jebao_aqua-homeassistant.git
cd jebao_aqua-homeassistant

# Create Home Assistant config directory
mkdir -p ../homeassistant-config
```

Your structure should look like:
```
~/ha-dev/jebao-dev/
├── jebao_aqua-homeassistant/      # Integration source code
│   └── custom_components/
│       └── jebao_aqua/
└── homeassistant-config/           # Home Assistant config
    └── custom_components/          # (will be created)
```

## Step 2: Create Docker Compose Configuration

Create `docker-compose.yml` in `~/ha-dev/jebao-dev/`:

```bash
cd ~/ha-dev/jebao-dev
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  homeassistant:
    container_name: ha-jebao-dev
    image: homeassistant/home-assistant:latest
    volumes:
      # Home Assistant configuration
      - ./homeassistant-config:/config
      # Mount integration source code directly (for live editing)
      - ./jebao_aqua-homeassistant/custom_components/jebao_aqua:/config/custom_components/jebao_aqua
    environment:
      - TZ=Europe/Vienna
    restart: unless-stopped
    network_mode: host
    privileged: true

EOF
```

**Why `network_mode: host`?**
- Allows HA to discover devices on your local network via UDP broadcast
- Enables direct TCP communication with Jebao devices
- No port mapping needed

## Step 3: Start Home Assistant

```bash
cd ~/ha-dev/jebao-dev

# Start Home Assistant
docker-compose up -d

# Watch logs (useful for debugging)
docker-compose logs -f homeassistant
```

**First startup takes 2-5 minutes** while Home Assistant initializes.

Access Home Assistant:
- URL: http://localhost:8123
- Create your first account when prompted

## Step 4: Configure Debug Logging

Create/edit `~/ha-dev/jebao-dev/homeassistant-config/configuration.yaml`:

```yaml
# Default config
default_config:

# Enable debug logging for Jebao integration
logger:
  default: info
  logs:
    custom_components.jebao_aqua: debug
    custom_components.jebao_aqua.api: debug
    custom_components.jebao_aqua.config_flow: debug
    custom_components.jebao_aqua.discovery: debug

# Recorder config (optional - prevents database bloat during testing)
recorder:
  purge_keep_days: 1
  commit_interval: 30
```

Restart Home Assistant:
```bash
docker-compose restart homeassistant
```

## Step 5: Install the Integration

1. **Via Home Assistant UI:**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Jebao Aqua Aquarium Pump"
   - Follow setup wizard

2. **Manual Config Entry (Alternative):**
   - Settings → Devices & Services → Integrations
   - Three dots menu → "Add Integration"

**Note:** Since we mounted the source code directly, any changes you make to the Python files will require a Home Assistant restart to take effect.

## Step 6: Development Workflow

### Making Code Changes

```bash
# 1. Edit files in your local repository
cd ~/ha-dev/jebao-dev/jebao_aqua-homeassistant/custom_components/jebao_aqua
vim api.py  # or use your preferred editor

# 2. Restart Home Assistant to load changes
docker-compose restart homeassistant

# 3. Watch logs for errors
docker-compose logs -f homeassistant

# 4. Test in Home Assistant UI
# Open http://localhost:8123
```

### Quick Restart Commands

```bash
# Restart HA (picks up code changes)
docker-compose restart homeassistant

# Stop HA
docker-compose stop

# Start HA
docker-compose start

# Rebuild and restart (if needed)
docker-compose down
docker-compose up -d

# View logs in real-time
docker-compose logs -f homeassistant

# View last 100 log lines
docker-compose logs --tail=100 homeassistant
```

### Accessing HA Container Shell

```bash
# Enter the container
docker exec -it ha-jebao-dev bash

# Check file structure
ls -la /config/custom_components/jebao_aqua/

# View logs from inside container
tail -f /config/home-assistant.log

# Exit container
exit
```

## Step 7: Testing Without Physical Devices

If you don't have physical Jebao devices, you can:

### Option 1: Mock Device Discovery

Create a test device mock (for development):

Edit `custom_components/jebao_aqua/discovery.py` temporarily:

```python
async def discover_devices():
    """Discover devices on the local network."""
    # TEMPORARY: Return mock device for testing
    return {
        "mock_device_123": "192.168.1.100"  # Fake device
    }
    
    # ... original code below (comment it out)
```

### Option 2: Skip LAN Requirements

You can test cloud-only functionality:
- Set up integration normally
- Leave LAN IP field empty during setup
- Integration will use cloud API only

### Option 3: API Testing Script

Create `test_api.py` in the repository root:

```python
import asyncio
import aiohttp
from custom_components.jebao_aqua.api import GizwitsApi
from custom_components.jebao_aqua.const import GIZWITS_API_URLS

async def test_login():
    """Test Gizwits API login."""
    email = "your_email@example.com"
    password = "your_password"
    region = "eu"  # or "us" or "cn"
    
    api = GizwitsApi(
        GIZWITS_API_URLS[region]["LOGIN_URL"],
        GIZWITS_API_URLS[region]["DEVICES_URL"],
        GIZWITS_API_URLS[region]["DEVICE_DATA_URL"],
        GIZWITS_API_URLS[region]["CONTROL_URL"],
    )
    
    async with api:
        token, error = await api.async_login(email, password)
        
        if token:
            print(f"✅ Login successful!")
            print(f"Token: {token[:20]}...")
            
            # Test getting devices
            api.set_token(token)
            devices = await api.get_devices()
            print(f"\n📱 Devices found: {len(devices.get('devices', []))}")
            
            for device in devices.get('devices', []):
                print(f"  - {device.get('dev_alias', 'Unnamed')}: {device.get('did')}")
        else:
            print(f"❌ Login failed: {error}")

if __name__ == "__main__":
    asyncio.run(test_login())
```

Run it:
```bash
cd ~/ha-dev/jebao-dev/jebao_aqua-homeassistant
python3 test_api.py
```

## Step 8: Debugging Tips

### View Integration Logs

```bash
# Real-time filtering for Jebao logs
docker-compose logs -f homeassistant | grep jebao_aqua

# Search for errors
docker-compose logs homeassistant | grep -i error | grep jebao

# Search for specific functions
docker-compose logs homeassistant | grep "get_device_data"
```

### Check Integration Status

Home Assistant UI:
- Settings → System → Logs
- Filter by "jebao_aqua"

Or via command line:
```bash
# View full log file
docker exec -it ha-jebao-dev cat /config/home-assistant.log | grep jebao_aqua
```

### Common Issues and Solutions

#### Issue: Integration not appearing

```bash
# Check if files are mounted correctly
docker exec -it ha-jebao-dev ls -la /config/custom_components/jebao_aqua/

# Expected output should show all .py files
# __init__.py, api.py, config_flow.py, etc.
```

#### Issue: Changes not taking effect

```bash
# Hard restart
docker-compose down
docker-compose up -d

# Clear cache (if needed)
docker exec -it ha-jebao-dev rm -rf /config/.storage/core.config_entries
# Warning: This removes ALL integrations, use carefully!
```

#### Issue: Import errors

```bash
# Check Python syntax
docker exec -it ha-jebao-dev python3 -m py_compile /config/custom_components/jebao_aqua/api.py

# Check for missing dependencies
docker exec -it ha-jebao-dev pip list | grep -i aiohttp
```

### Network Debugging

Test device connectivity:
```bash
# From your host machine
nc -v DEVICE_IP 12416

# From HA container
docker exec -it ha-jebao-dev nc -v DEVICE_IP 12416

# Test UDP broadcast
docker exec -it ha-jebao-dev bash
apt-get update && apt-get install -y netcat
echo -ne '\x00\x00\x00\x03\x03\x00\x00\x03' | nc -u -b 255.255.255.255 12414
```

## Step 9: VS Code Integration (Optional)

For better development experience:

1. **Install VS Code Extensions:**
   - Python
   - Docker
   - Home Assistant Config Helper

2. **Open Project in VS Code:**
```bash
code ~/ha-dev/jebao-dev
```

3. **Create `.vscode/settings.json`:**
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.associations": {
        "*.yaml": "home-assistant"
    }
}
```

## Step 10: Testing Checklist

Before committing changes:

- [ ] Code changes made
- [ ] HA restarted: `docker-compose restart homeassistant`
- [ ] No errors in logs
- [ ] Integration loads successfully
- [ ] Entities created correctly
- [ ] Controls work (if testable)
- [ ] Status updates properly
- [ ] Code formatted: `black custom_components/jebao_aqua/`
- [ ] No debug print statements left

## Useful Docker Commands Reference

```bash
# View container status
docker-compose ps

# View resource usage
docker stats ha-jebao-dev

# Clean up (removes container and volumes)
docker-compose down -v

# Update Home Assistant image
docker-compose pull
docker-compose up -d

# View container configuration
docker inspect ha-jebao-dev

# Backup configuration
tar -czf ha-config-backup.tar.gz homeassistant-config/

# Restore configuration
tar -xzf ha-config-backup.tar.gz
```

## Cleanup

When you're done with development:

```bash
cd ~/ha-dev/jebao-dev

# Stop and remove container
docker-compose down

# Remove volumes (deletes all HA data)
docker-compose down -v

# Remove entire development directory (careful!)
cd ~
rm -rf ~/ha-dev/jebao-dev
```

## Next Steps

Now that you have a working development environment:

1. ✅ Read through the integration code
2. ✅ Make small test changes to understand the flow
3. ✅ Set up with real devices (if available)
4. ✅ Try adding a new device model
5. ✅ Implement bug fixes or features
6. ✅ Consult MAINTENANCE_GUIDE.md for detailed information

## Troubleshooting Development Environment

### Port 8123 Already in Use

```bash
# Find what's using the port
lsof -i :8123

# Kill the process (if safe)
kill -9 PID

# Or change the port in docker-compose.yml
# Replace network_mode: host with:
ports:
  - "8124:8123"  # Use different host port
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/ha-dev/jebao-dev

# Or run with sudo (not recommended)
sudo docker-compose up -d
```

### Network Discovery Not Working

If using bridged network instead of host mode:
```yaml
# In docker-compose.yml, replace network_mode with:
ports:
  - "8123:8123"
  - "12414:12414/udp"  # Discovery
  - "12416:12416/tcp"  # Device communication
```

---

**Questions or Issues?** Refer to MAINTENANCE_GUIDE.md or open an issue on GitHub.