// Server: Serves the frontend and handles MQTT connection
const express = require('express');
const mqtt = require('mqtt');

const app = express();
const MQTT_BROKER = 'mqtt:fancyguysdev.de'; // Replace with your broker
const MQTT_TOPIC = 'led/effect'; // Replace with your topic
const mqttClient = mqtt.connect(MQTT_BROKER);

// Serve static files
app.use(express.static('public'));
app.use(express.json()); // Middleware to parse JSON body

// Endpoint to handle effect selection
app.post('/send-effect', (req, res) => {
    const { effect } = req.body;

    if (!effect) {
        return res.status(400).json({ success: false, error: 'Effect is required.' });
    }

    mqttClient.publish(MQTT_TOPIC, JSON.stringify({ effect }), (err) => {
        if (err) {
            console.error('Failed to publish effect:', err);
            return res.status(500).json({ success: false, error: 'Failed to send effect to MQTT.' });
        }
        console.log(`Effect "${effect}" sent to topic "${MQTT_TOPIC}"`);
        res.json({ success: true });
    });
});

// MQTT connection
mqttClient.on('connect', () => {
    console.log('Connected to MQTT broker');
});

mqttClient.on('error', (err) => {
    console.error('MQTT connection error:', err);
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
