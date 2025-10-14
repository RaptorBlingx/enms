/**
 * ============================================================================
 * EnMS - Node-RED Settings
 * Configuration for Data Pipeline
 * ============================================================================
 */

module.exports = {
    // Flow file settings
    flowFile: 'flows.json',
    flowFilePretty: true,
    
    // Credential encryption
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || "enms-node-red-secret-key-change-in-production",
    
    // Admin UI settings
    adminAuth: {
        type: "credentials",
        users: [{
            username: process.env.NODE_RED_USERNAME || "admin",
            password: process.env.NODE_RED_PASSWORD_HASH || "$2b$08$wKXiKXKZ4v0g.iBZ6Y5B1.VJCHZqJV8XvPLXsNxMHjWKGqT0uLM4S", // "admin"
            permissions: "*"
        }]
    },
    
    // HTTP settings
    uiPort: process.env.PORT || 1880,
    uiHost: "0.0.0.0",
    
    // HTTPS settings (disabled for now, can be enabled in production)
    // https: {
    //     key: require("fs").readFileSync('/path/to/privkey.pem'),
    //     cert: require("fs").readFileSync('/path/to/cert.pem')
    // },
    
    // HTTP request settings
    httpRequestTimeout: 120000,
    
    // HTTP Admin API
    httpAdminRoot: '/admin',
    httpAdminCors: {
        origin: "*",
        credentials: true
    },
    
    // HTTP Node endpoints
    httpNodeRoot: '/',
    httpNodeCors: {
        origin: "*",
        credentials: true
    },
    
    // Runtime settings
    runtimeState: {
        enabled: false,
        ui: false,
    },
    
    // Logging
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        },
        file: {
            level: "info",
            metrics: false,
            audit: false,
            handler: require.resolve("./file-log-handler")
        }
    },
    
    // Context storage
    contextStorage: {
        default: {
            module: "memory"
        },
        file: {
            module: "localfilesystem"
        }
    },
    
    // Export settings
    exportGlobalContextKeys: false,
    
    // Editor settings
    editorTheme: {
        projects: {
            enabled: false
        },
        palette: {
            catalogues: [
                'https://catalogue.nodered.org/catalogue.json'
            ]
        },
        header: {
            title: "EnMS Data Pipeline",
            image: null,
            url: null
        },
        menu: {
            "menu-item-help": {
                label: "EnMS Documentation",
                url: "/docs"
            }
        }
    },
    
    // Function node settings
    functionGlobalContext: {
        // Global objects available to function nodes
        os: require('os'),
        moment: require('moment')
    },
    
    // Function external modules
    functionExternalModules: true,
    
    // Node settings
    nodeMessageBufferMaxLength: 0,
    
    // Debug settings
    debugMaxLength: 1000,
    debugUseColors: true,
    
    // UI settings
    ui: {
        path: "ui"
    },
    
    // MQTT settings (for reference, actual config in nodes) - Host Mosquitto Broker
    mqtt: {
        broker: process.env.MQTT_HOST || "172.18.0.1",
        port: parseInt(process.env.MQTT_PORT || "1883"),
        username: process.env.MQTT_USERNAME || "raptorblingx",
        password: process.env.MQTT_PASSWORD || "raptorblingx"
    },
    
    // PostgreSQL settings (for reference)
    postgres: {
        host: process.env.POSTGRES_HOST || "postgres",
        port: parseInt(process.env.POSTGRES_PORT || "5432"),
        database: process.env.POSTGRES_DB || "enms",
        user: process.env.POSTGRES_USER || "raptorblingx",
        password: process.env.POSTGRES_PASSWORD || "raptorblingx"
    }
};