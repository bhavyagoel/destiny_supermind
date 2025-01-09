export default function handler(req, res) {
    if (req.method === 'GET') {
      res.status(200).json({ status: 'ok', uptime: process.uptime(), timestamp: Date.now() });
    } else {
      res.setHeader('Allow', ['GET']);
      res.status(405).json({ error: `Method ${req.method} Not Allowed` });
    }
  }
  