// app.ts
import express, {
  Express,
  Router,
  Response as ExResponse,
  Request as ExRequest,
  ErrorRequestHandler,
} from 'express';

import swaggerUi from 'swagger-ui-express';
// import { RegisterRoutes } from '../build/routes';

import cors from 'cors';

// Create the Express app
const app: Express = express();

// Express middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// In your server or middleware setup
app.use(
  cors({
    origin: 'http://localhost:5173', // Vite default from the frontend
    credentials: true, // Allow cookies to be sent
  })
);

// Swagger documentation setup
app.use(
  '/api/v0/docs',
  swaggerUi.serve,
  async (_req: ExRequest, res: ExResponse) => {
    let swaggerSpec;
    try {
      swaggerSpec = require('./swagger.json'); // relative to compiled build folder, made with tsoa
    } catch (error) {
      return res.status(500).send('Swagger spec not found');
    }
    return res.send(swaggerUi.generateHTML(swaggerSpec));
  }
);

// Register API routes
const router = Router();
try {
  const { RegisterRoutes } = require('./routes'); // relative to compiled build folder
  RegisterRoutes(router);
} catch (error) {
  console.error('Error loading routes:', error);
}
app.use('/api/v0', router);

// Error handling middleware
const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  res.status(err.status || 500).json({
    message: err.message || 'Internal Server Error',
    errors: err.errors || [],
    status: err.status || 500,
  });
};
app.use(errorHandler);

export default app;