# 🚀 Quick Start - Get Running in 5 Minutes

This guide will get your Docker-based Home Assistant development environment up and running immediately.

## Prerequisites Check

```bash
# Make sure you have Docker installed
docker --version
# Should show: Docker version 20.x.x or higher

# Make sure you're in the project directory
pwd
# Should end with: jebao_aqua-homeassistant-2
```

## Step 1: Start Home Assistant (1 minute)

```bash
# Start Home Assistant container
docker-compose up -d

# Watch the startup logs (optional)
docker-compose logs -f homeassistant
```

**Wait for this message in logs:**
```
INFO (MainThread) [homeassistant.bootstrap] Home Assistant initialized in X.XXs
```

Press `Ctrl+C` to stop watching logs (container keeps running).

**First startup takes 2-5 minutes** to download the image and initialize.

## Step 2: Access Home Assistant (30 seconds)

1. Open your browser: **http://localhost:8123**
2. Create your first account (username and password)
3. Set up basic preferences (location, timezone, etc.)

## Step 3: Install Jebao Aqua Integration (2 minutes)

The integration is already mounted in the container!

1. In Home Assistant UI, go to: **Settings** → **Devices & Services**
2. Click the **"+ Add Integration"** button (bottom right)
3. Search for: **"Jebao Aqua"**
4. Click on **"Jebao Aqua Aquarium Pump"**
5. Follow the setup wizard:
   - Select your country
   - Enter your Jebao Aqua app credentials
   - Wait for device discovery (or enter IP manually)

## Step 4: Start Developing! (∞)

### Make Code Changes

```bash
# Edit any Python file in the integration
vim custom_components/jebao_aqua/api.py

# Restart Home Assistant to load changes
docker-compose restart homeassistant

# Watch logs for errors
docker-compose logs -f homeassistant | grep jebao_aqua
```

### View Debug Logs

- In Home Assistant: **Settings** → **System** → **Logs**
- Filter by "jebao_aqua" to see integration logs
- Or use command line: `docker-compose logs -f homeassistant | grep jebao`

### Common Commands

```bash
# Restart HA (after code changes)
docker-compose restart homeassistant

# Stop HA
docker-compose stop

# Start HA (after stopping)
docker-compose start

# View logs
docker-compose logs -f homeassistant

# Stop and remove everything
docker-compose down

# Access container shell
docker exec -it ha-jebao-dev bash
```

## Quick Troubleshooting

### Port 8123 already in use?
```bash
# Find what's using it
lsof -i :8123

# Kill that process or change port in docker-compose.yml
```

### Integration not showing up?
```bash
# Check if files are mounted
docker exec -it ha-jebao-dev ls /config/custom_components/jebao_aqua/

# Should list: __init__.py, api.py, config_flow.py, etc.
```

### Changes not taking effect?
```bash
# Hard restart
docker-compose down
docker-compose up -d
```

## What's Next?

- 📖 Read **DEVELOPMENT_SETUP.md** for detailed setup information
- 📘 Check **MAINTENANCE_GUIDE.md** for comprehensive documentation
- 📄 See **QUICK_START.md** for maintenance reference
- 🐛 Start debugging and testing the integration!

## Development Workflow Example

```bash
# 1. Edit code
vim custom_components/jebao_aqua/api.py

# 2. Restart HA
docker-compose restart homeassistant

# 3. Check logs for errors
docker-compose logs --tail=50 homeassistant | grep -i error

# 4. Test in UI
# Open http://localhost:8123 and test your changes

# 5. Commit when working
git add .
git commit -m "Fix: Updated API handling"
```

## Directory Structure

```
jebao_aqua-homeassistant-2/
├── START_HERE.md              ← You are here!
├── DEVELOPMENT_SETUP.md       ← Detailed setup guide
├── MAINTENANCE_GUIDE.md       ← Full documentation
├── QUICK_START.md            ← Maintainer reference
├── docker-compose.yml         ← Docker config
├── ha-config/                 ← Home Assistant config
│   ├── configuration.yaml     ← Main HA config
│   └── ...
└── custom_components/         ← Integration source
    └── jebao_aqua/
        ├── __init__.py
        ├── api.py
        └── ...
```

## Need Help?

- 🔧 **Setup Issues**: See DEVELOPMENT_SETUP.md
- 📚 **How it works**: See MAINTENANCE_GUIDE.md
- ⚡ **Quick reference**: See QUICK_START.md
- 🐛 **Report bugs**: GitHub Issues

---

**Ready to go?** Run `docker-compose up -d` and open http://localhost:8123 🎉