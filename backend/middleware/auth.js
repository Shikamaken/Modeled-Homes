// backend/middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Please log in to access this resource.' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // ✅ Attach userId and uuid for user-specific operations
    req.user = {
      userId: decoded.userId,
      uuid: decoded.uuid, // ✅ Now accessible for directory structure
    };

    next();
  } catch (error) {
    console.error("Token verification error:", error); // Log details server-side
    res.status(401).json({ message: 'Your session has expired. Please log in again.' });
  }
};