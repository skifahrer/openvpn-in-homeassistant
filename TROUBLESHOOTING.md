# Troubleshooting - Integration Not Showing

## Problem: Can't Find OpenVPN Manager Integration After HACS Install

### Step 1: Verify Files Are Installed

**Check via File Editor (if you have it):**
1. Go to **Settings → Add-ons → File editor**
2. Browse to `/config/custom_components/`
3. You should see a folder: `openvpn_manager`
4. Inside it should be: `__init__.py`, `manifest.json`, `config_flow.py`, etc.

**Or via SSH:**
```bash
ls -la /config/custom_components/openvpn_manager/
```

**Expected files:**
```
__init__.py
config_flow.py
const.py
manifest.json
sensor.py
switch.py
strings.json
helpers/
  __init__.py
  api_client.py
translations/
  en.json
```

### Step 2: Restart Home Assistant Properly

**Important: Must do FULL restart, not just reload!**

1. Go to **Settings → System**
2. Click **Restart** (top right)
3. Select **Restart Home Assistant**
4. Wait 1-2 minutes for full restart

### Step 3: Check Home Assistant Logs

After restart, check for errors:

1. Go to **Settings → System → Logs**
2. Search for "openvpn" or "openvpn_manager"
3. Look for any error messages

**Common errors:**
- `Invalid manifest` - manifest.json has errors
- `Import error` - Python syntax error
- `Module not found` - missing files

### Step 4: Clear Browser Cache

Sometimes the browser caches the integration list:

1. **Hard refresh:** Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. **Or clear cache:**
   - Chrome/Edge: `Ctrl+Shift+Delete` → Clear cached images and files
   - Firefox: `Ctrl+Shift+Delete` → Cached Web Content
   - Safari: `Cmd+Option+E`
3. Close and reopen browser
4. Log back into Home Assistant

### Step 5: Try Adding Integration Again

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. In the search box, type: `openvpn`
4. Should see: **"OpenVPN Manager"** with blue icon

**Still not showing?** Continue to Step 6.

### Step 6: Force Re-download via HACS

1. Open **HACS → Integrations**
2. Find **OpenVPN Manager** in your installed list
3. Click on it
4. Click the **3-dot menu** (⋮) → **Redownload**
5. Wait for completion
6. **Restart Home Assistant** again (Settings → System → Restart)
7. Wait 2 minutes
8. Try adding integration again

### Step 7: Check Integration Loads

**Via Developer Tools:**

1. Go to **Developer Tools → Services**
2. In the service dropdown, start typing "openvpn"
3. If integration loaded, you might see some services (or at least the integration domain exists)

**Via Logs:**

Look for this line in logs (Settings → System → Logs):
```
Setting up openvpn_manager
```

If you see it, the integration loaded successfully.

### Step 8: Manual Verification

**Check if manifest.json is valid:**

1. Open `/config/custom_components/openvpn_manager/manifest.json`
2. Verify it starts with:
```json
{
  "domain": "openvpn_manager",
  "name": "OpenVPN Manager",
```

**Check if __init__.py exists:**

Should exist at: `/config/custom_components/openvpn_manager/__init__.py`

### Step 9: Try Manual Installation

If HACS keeps failing, install manually:

1. Download the repository as ZIP from GitHub
2. Extract it
3. Copy `custom_components/openvpn_manager` to `/config/custom_components/`
4. Restart Home Assistant
5. Try adding integration

## Quick Checklist

- [ ] Files installed at `/config/custom_components/openvpn_manager/`
- [ ] Home Assistant restarted (full restart, not reload)
- [ ] Browser cache cleared
- [ ] No errors in logs for "openvpn_manager"
- [ ] Waited 2 minutes after restart
- [ ] Searched for "openvpn" in Add Integration dialog

## Common Issues

### Issue: "Integration not found"
**Cause:** Files not installed or wrong location
**Fix:** Verify files exist, reinstall via HACS

### Issue: "Setup failed"
**Cause:** Python errors in code
**Fix:** Check logs, report error with log details

### Issue: Shows up but can't configure
**Cause:** Add-on not running
**Fix:** Install and start the OpenVPN Manager add-on first

## Still Not Working?

If integration still doesn't show after all these steps:

1. **Check logs and share error:**
   - Settings → System → Logs
   - Search for "openvpn"
   - Screenshot any errors

2. **Verify Home Assistant version:**
   - Settings → About
   - Must be 2024.1.0 or newer

3. **Report issue:**
   - Go to: https://github.com/skifahrer/openvpn-in-homeassistant/issues
   - Include:
     - Home Assistant version
     - Installation method (HACS/manual)
     - Log errors
     - Steps you tried

## Expected Working Flow

When everything works correctly:

1. **HACS Install** → Files copied to `/config/custom_components/openvpn_manager/`
2. **Restart HA** → Integration loads, registers domain
3. **Add Integration** → Shows "OpenVPN Manager" in search
4. **Configure** → Enter API host/port
5. **Success** → Integration added, entities appear

If any step fails, that's where the problem is!
