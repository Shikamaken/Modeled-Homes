// backend/routes/hvac.js
const router = require('express').Router();
const hvacController = require('../controllers/hvacController');
const auth = require('../middleware/auth');

router.post('/projects', auth, hvacController.createProject);
router.get('/projects', auth, hvacController.getProjects);
router.put('/projects/:id', auth, hvacController.updateProject);
router.delete('/projects/:id', auth, hvacController.deleteProject);

// Add other relevant routes

module.exports = router;