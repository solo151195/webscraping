# Configuration
TIMEOUT = 30000  # Default timeout for waits (ms)
MIN_DELAY = 0.3   # Minimum human-like delay (s)
MAX_DELAY = 0.5   # Maximum human-like delay (s)
TYPING_DELAY = (50, 150)  # Typing delay range (ms)

stealth_script_firefox = """
    // ----- WebDriver Detection Fix -----
    // Completely remove webdriver property
    Object.defineProperty(Object.getPrototypeOf(navigator), 'webdriver', {
        get: () => undefined,
        configurable: true
    });
    
    window.chrome = {
        runtime: {},
        loadTimes: () => {},
        csi: () => {},
        app: {},
        webstore: {}
    };

    // Delete any other webdriver indicators
    delete navigator.__proto__.webdriver;

    // ----- PluginArray Fix -----
    // Create a proper PluginArray with correct prototype chain
    const fakePlugins = Object.create(PluginArray.prototype);
    const flashPlugin = Object.create(Plugin.prototype);

    Object.defineProperties(flashPlugin, {
        '0': {
            value: {
                type: "application/x-shockwave-flash",
                suffixes: "swf",
                description: "Shockwave Flash", 
                enabledPlugin: null
            },
            enumerable: true
        },
        'description': {
            value: "Shockwave Flash",
            enumerable: true
        },
        'filename': {
            value: "libflashplayer.so",
            enumerable: true
        },
        'length': {
            value: 1,
            enumerable: true
        },
        'name': {
            value: "Shockwave Flash",
            enumerable: true
        }
    });

    // Make the fake plugin "array-like"
    Object.defineProperties(fakePlugins, {
        '0': {
            value: flashPlugin,
            enumerable: true
        },
        'length': {
            value: 1,
            enumerable: true
        }
    });

    // Attach required methods
    fakePlugins.item = function(index) {
        return this[index] || null;
    };

    fakePlugins.namedItem = function(name) {
        for (let i = 0; i < this.length; i++) {
            if (this[i].name === name) {
                return this[i];
            }
        }
        return null;
    };

    fakePlugins.refresh = function() {};

    // Override navigator.plugins with our fake implementation
    Object.defineProperty(navigator, 'plugins', {
        get: () => fakePlugins,
        enumerable: true,
        configurable: true
    });

    // Check and fix MimeType related properties
    if (!navigator.mimeTypes || navigator.mimeTypes.length === 0) {
        const fakeMimeTypes = Object.create(MimeTypeArray.prototype);
        const flashMimeType = Object.create(MimeType.prototype);

        Object.defineProperties(flashMimeType, {
            'type': {
                value: 'application/x-shockwave-flash',
                enumerable: true
            },
            'suffixes': {
                value: 'swf',
                enumerable: true
            },
            'description': {
                value: 'Shockwave Flash',
                enumerable: true
            },
            'enabledPlugin': {
                value: flashPlugin,
                enumerable: true
            }
        });

        Object.defineProperties(fakeMimeTypes, {
            'length': {
                value: 1,
                enumerable: true
            },
            '0': {
                value: flashMimeType,
                enumerable: true
            },
            'application/x-shockwave-flash': {
                value: flashMimeType,
                enumerable: true
            }
        });

        fakeMimeTypes.item = function(index) {
            return this[index] || null;
        };

        fakeMimeTypes.namedItem = function(name) {
            return this[name] || null;
        };

        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => fakeMimeTypes,
            enumerable: true,
            configurable: true
        });
        // Disable WebRTC (Prevent IP Leak)
        const originalRTCPeerConnection = window.RTCPeerConnection;
        window.RTCPeerConnection = function(...args) {
            console.log('Blocked WebRTC');
            return null;
        };
    }
    """

stealth_script_chromium = """
(() => {
  // --- navigator.webdriver ---
  Object.defineProperty(Object.getPrototypeOf(navigator), 'webdriver', {
    get: () => undefined,
    configurable: true
  });

  // --- window.chrome ---
  window.chrome = {
    runtime: {},
    loadTimes: () => {},
    csi: () => {},
    app: {},
    webstore: {}
  };

  // --- PluginArray ---
  const fakePlugin = Object.create(Plugin.prototype);
  Object.defineProperties(fakePlugin, {
    0: {
      value: {
        type: "application/x-pdf",
        suffixes: "pdf",
        description: "Portable Document Format",
        enabledPlugin: null
      },
      enumerable: true
    },
    description: {
      value: "Chrome PDF Plugin",
      enumerable: true
    },
    filename: {
      value: "internal-pdf-viewer",
      enumerable: true
    },
    length: {
      value: 1,
      enumerable: true
    },
    name: {
      value: "Chrome PDF Plugin",
      enumerable: true
    }
  });

  const fakePlugins = Object.create(PluginArray.prototype);
  Object.defineProperties(fakePlugins, {
    0: {
      value: fakePlugin,
      enumerable: true
    },
    length: {
      value: 1,
      enumerable: true
    }
  });
  fakePlugins.item = function (index) {
    return this[index] || null;
  };
  fakePlugins.namedItem = function (name) {
    for (let i = 0; i < this.length; i++) {
      if (this[i].name === name) {
        return this[i];
      }
    }
    return null;
  };
  fakePlugins.refresh = function () {};

  Object.defineProperty(navigator, 'plugins', {
    get: () => fakePlugins,
    configurable: true
  });

  // --- MimeTypeArray ---
  const fakeMimeType = Object.create(MimeType.prototype);
  Object.defineProperties(fakeMimeType, {
    type: { value: "application/x-pdf", enumerable: true },
    suffixes: { value: "pdf", enumerable: true },
    description: { value: "Portable Document Format", enumerable: true },
    enabledPlugin: { value: fakePlugin, enumerable: true }
  });

  const fakeMimeTypes = Object.create(MimeTypeArray.prototype);
  Object.defineProperties(fakeMimeTypes, {
    0: { value: fakeMimeType, enumerable: true },
    "application/x-pdf": { value: fakeMimeType, enumerable: true },
    length: { value: 1, enumerable: true }
  });
  fakeMimeTypes.item = function(index) {
    return this[index] || null;
  };
  fakeMimeTypes.namedItem = function(name) {
    return this[name] || null;
  };

  Object.defineProperty(navigator, 'mimeTypes', {
    get: () => fakeMimeTypes,
    configurable: true
  });

  // --- Permissions API ---
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => {
    if (parameters?.name === 'notifications') {
      return Promise.resolve({ 
        state: Notification?.permission || 'default',
        onchange: null
      });
    }
    return originalQuery(parameters);
  };
  window.navigator.permissions.query.toString = () => 'function query() { [native code] }';

  // --- Notification.permission ---
  Object.defineProperty(Notification, 'permission', {
    get: () => 'default'
  });

  // --- Spoof languages and platform ---
  Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
    configurable: true
  });
  Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32',
    configurable: true
  });

  // --- HTMLVideoElement.canPlayType ---
  const canPlayTypeBackup = HTMLVideoElement.prototype.canPlayType;
  HTMLVideoElement.prototype.canPlayType = function(type) {
    if (type === 'video/mp4' || type === 'video/h264' || type.includes('avc1')) {
      return 'maybe';
    }
    return canPlayTypeBackup.call(this, type);
  };
})();
"""


CHROME_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]
firefox_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'
]
screen_resolutions = [
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768},
    {'width': 1536, 'height': 864},
    {'width': 1440, 'height': 900},
    {'width': 1280, 'height': 720}
]
firefox_user_prefs = {
        # Disable webdriver flag
        'dom.webdriver.enabled': False,
        'dom.automation.enabled': False,
        # Additional Marionette/remote settings that might expose automation
        'marionette.enabled': False,
        'marionette.port': 0,
        'remote.enabled': False,
        'remote.active': False,
        'remote.force-local': False,
        # Privacy settings that might help with fingerprinting
        'privacy.trackingprotection.enabled': False,
        # Recommended to keep false as true can break some websites
        'privacy.resistFingerprinting': False,
        # Disable features that might expose automation
        'media.navigator.permission.disabled': True,
        'permissions.default.camera': 2,
        'permissions.default.microphone': 2,
        # Disable Firefox-specific telemetry and reporting
        'toolkit.telemetry.enabled': False,
        'datareporting.policy.dataSubmissionEnabled': False,
        'browser.ping-centre.telemetry': False,
        # Browser behavior settings
        'network.http.referer.XOriginPolicy': 0,
        'network.cookie.cookieBehavior': 0,
        # Disable Firefox update notifications
        'app.update.enabled': False,
        # WebRTC settings
        'media.peerconnection.enabled': True,
        # Make sure plugins can be enumerated properly
        'plugin.state.flash': 2
    }