// index.js (Node.js server excerpt)
const express = require('express');
const { Server } = require('socket.io');
const http = require('http');
const mqtt = require('mqtt');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const MQTT_BROKER = 'mqtt://fancyguysdev.de';
const LED_EFFECT_TOPIC = 'led/effect';
const LED_SAVE_DEFAULT_TOPIC = 'led/effect/save-default';
const LED_CLIENTS_TOPIC = 'led/clients';
const LED_EFFECTS_LIST_TOPIC_PREFIX = 'led/effects/';

const mqttClient = mqtt.connect(MQTT_BROKER);
const connectedClients = new Set();
const clientEffectsMap = {};

app.use(express.static('public'));
app.use(express.json());

// Returns list of clients
app.get('/api/clients', (req, res) => {
    res.json(Array.from(connectedClients));
});

// Returns effects for a given client
app.get('/api/effects/:clientId', (req, res) => {
    const clientId = req.params.clientId;
    const effects = clientEffectsMap[clientId] || [];
    res.json(effects);
});

// Send effect
app.post('/send-effect', (req, res) => {
    const { client_id, effect_name, config } = req.body;
    if (!client_id || !effect_name) {
        return res.status(400).json({ success: false, error: 'client_id and effect_name are required.' });
    }
    const payload = {
        client_id,
        effect_name,
        config: {}
    };
    mqttClient.publish(LED_EFFECT_TOPIC, JSON.stringify(payload), err => {
        if (err) {
            console.error('Failed to publish effect:', err);
            return res.status(500).json({ success: false, error: 'Failed to send effect to MQTT.' });
        }
        console.log(`Effect "${effect_name}" for "${client_id}" sent.`);
        res.json({ success: true });
    });
});

// Save default
app.post('/save-default', (req, res) => {
    const { client_id, effect_name, config } = req.body;
    if (!client_id || !effect_name) {
        return res.status(400).json({ success: false, error: 'client_id and effect_name are required.' });
    }
    const payload = {
        client_id,
        effect_name,
        config: config || {}
    };
    mqttClient.publish(LED_SAVE_DEFAULT_TOPIC, JSON.stringify(payload), err => {
        if (err) {
            console.error('Failed to publish default config:', err);
            return res.status(500).json({ success: false, error: 'Failed to send default config.' });
        }
        console.log(`Default config for effect "${effect_name}" of "${client_id}" saved.`);
        res.json({ success: true });
    });
});

// MQTT setup
mqttClient.on('connect', () => {
    console.log('Connected to MQTT broker (Node server)');
    mqttClient.subscribe(LED_CLIENTS_TOPIC);
    mqttClient.subscribe(`${LED_EFFECTS_LIST_TOPIC_PREFIX}#`);
});

mqttClient.on('message', (topic, message) => {
    if (topic === LED_CLIENTS_TOPIC) {
        try {
            const { client_id, status } = JSON.parse(message.toString());
            console.log(`${client_id}: ${status}`)
            if (status === 'connected') {
                connectedClients.add(client_id);
            } else if (status === 'disconnected') {
                connectedClients.delete(client_id);
            }
            io.emit('clients_updated', Array.from(connectedClients));
        } catch (err) {
            console.error('Error processing client list message:', err);
        }
    } else if (topic.startsWith(LED_EFFECTS_LIST_TOPIC_PREFIX)) {
        try {
            const payload = JSON.parse(message.toString());
            const { client_id, effects } = payload;
            clientEffectsMap[client_id] = effects || [];
        } catch (err) {
            console.error('Error processing effects list message:', err);
        }
    }
});

// Socket.io
io.on('connection', (socket) => {
    socket.emit('clients_updated', Array.from(connectedClients));
});

server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
