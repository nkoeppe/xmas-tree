const express = require('express');
const { Server } = require('socket.io');
const http = require('http');
const mqtt = require('mqtt');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const MQTT_BROKER = 'mqtt://fancyguysdev.de';
const LED_EFFECT_TOPIC = 'led/effect';
const LED_CLIENTS_TOPIC = 'led/clients';

const mqttClient = mqtt.connect(MQTT_BROKER);
const connectedClients = new Set();

app.use(express.static('public'));
app.use(express.json());

// Returns the list of currently connected LED strips
app.get('/api/clients', (req, res) => {
    res.json(Array.from(connectedClients));
});

// Handles effect selection
app.post('/send-effect', (req, res) => {
    const { client_id, effect_name, config } = req.body;
    if (!client_id || !effect_name) {
        return res.status(400).json({ success: false, error: 'client_id and effect_name are required.' });
    }
    const payload = JSON.stringify({ client_id, effect_name, config: config || {} });
    mqttClient.publish(LED_EFFECT_TOPIC, payload, err => {
        if (err) {
            console.error('Failed to publish effect:', err);
            return res.status(500).json({ success: false, error: 'Failed to send effect to MQTT.' });
        }
        console.log(`Effect "${effect_name}" for "${client_id}" sent to "${LED_EFFECT_TOPIC}"`);
        res.json({ success: true });
    });
});

// MQTT setup
mqttClient.on('connect', () => {
    console.log('Connected to MQTT broker');
    mqttClient.subscribe(LED_CLIENTS_TOPIC);
    mqttClient.subscribe(LED_EFFECT_TOPIC);
});

mqttClient.on('message', (topic, message) => {
    if (topic === LED_CLIENTS_TOPIC) {
        try {
            const { client_id, status } = JSON.parse(message.toString());
            if (status === 'connected') {
                connectedClients.add(client_id);
            } else if (status === 'disconnected') {
                connectedClients.delete(client_id);
            }
            io.emit('clients_updated', Array.from(connectedClients));
            console.log('Updated clients:', Array.from(connectedClients));
        } catch (err) {
            console.error('Error processing client list message:', err);
        }
    }
});

// Socket.io connections
io.on('connection', (socket) => {
    socket.emit('clients_updated', Array.from(connectedClients));
});

server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
