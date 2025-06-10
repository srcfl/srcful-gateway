import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Srcful Energy Gateway', () => {
  render(<App />);
  const headerElement = screen.getByText(/Srcful Energy Gateway/i);
  expect(headerElement).toBeInTheDocument();
}); 