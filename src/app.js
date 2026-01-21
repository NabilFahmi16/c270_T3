const express = require('express');
const app = express();
app.use(express.json());

let todos = []; // In-memory storage (for demo; real app would use DB)

// Backlog feature 1: Add todo
app.post('/todos', (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ error: 'Title required' });
  const todo = { id: todos.length + 1, title, completed: false };
  todos.push(todo);
  res.status(201).json(todo);
});

// Core: List all todos
app.get('/todos', (req, res) => {
  res.json(todos);
});

// Backlog feature 2: Search todos by title
app.get('/todos/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(400).json({ error: 'Query required' });
  const results = todos.filter(todo => todo.title.toLowerCase().includes(q.toLowerCase()));
  res.json(results);
});

// Backlog feature 3: Delete todo
app.delete('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  todos = todos.filter(todo => todo.id !== id);
  res.status(204).send();
});

// Health check for Kubernetes liveness probe
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

module.exports = app; // For testing

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
