import { render, screen, fireEvent } from '@testing-library/react';
import HomePage from './HomePage';

test('renders homepage and interacts correctly', () => {
  render(<HomePage />);
  const input = screen.getByLabelText(/what do you want to buy?/i);
  fireEvent.change(input, { target: { value: 'I want to furnish a study room' } });
  const button = screen.getByText(/submit/i);
  fireEvent.click(button);
  const followUpQuestion = screen.getByText(/what is your budget?/i);
  expect(followUpQuestion).toBeInTheDocument();
});
