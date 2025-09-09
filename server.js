require('dotenv').config();
const express = require('express');
const miio = require('node-miio');

const ROBOT_IP = process.env.ROBOT_IP ;
const ROBOT_TOKEN = process.env.ROBOT_TOKEN;

const app = express();
app.use(express.json());

const COMMANDS_CONFIG = {
  start_cleaning: { method: 'app_start' },
  pause_cleaning: { method: 'app_pause' },
  stop_cleaning:  { method: 'app_pause' },
  dock:           { method: 'app_charge' },
  spot:           { method: 'app_spot' },
  goto:           { method: 'app_goto_target', needsParams: true },
};

let device;

const getDevice = async () => {
  if (!device) {
    device = await miio.device({ address: ROBOT_IP, token: ROBOT_TOKEN });
  }
  return device;
}

app.get('/info', async (_req, res) => {
  try {
    const deivce = await getDevice();
    const info = await deivce.call('miIO.info'); 

    const result = {
      model: deivce.model || info.model,
      firmware: info.fw_ver,
      mac: info.mac,
      token: ROBOT_TOKEN,
    };

    res.json({ ok: true, ...result });
  } catch (e) {
    console.error('Error fetching device info', e);
    res.status(500).json({ ok: false, error: `TOKEN: ${process.env.ROBOT_TOKEN}` });
  }
});


app.post('/roborock-command', async (req, res) => {
  try {
    const { command, params } = req.body || {};
    const availableCommand = COMMANDS_CONFIG[command];
    if (!availableCommand) {
      return res.status(400).json({ ok:false, error:'Invalid command', allowed:Object.keys(COMMANDS_CONFIG) });
    }

    const device = await getDevice();
    const result = await device.call(availableCommand.method, availableCommand.needsParams ? params : []);
    res.json({ ok:true, result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok:false, error: err.message || String(err) });
  }
});

const port = process.env.PORT || 8000;
app.listen(port, () => console.log(`Server is running on port: ${port}`));
