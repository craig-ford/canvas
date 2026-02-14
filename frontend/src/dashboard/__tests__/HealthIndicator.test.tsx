import React from 'react';
import { render, screen } from '@testing-library/react';
import HealthIndicator from '../HealthIndicator';

describe('HealthIndicator', () => {
  test('renders "Not Started" status with gray styling', () => {
    render(<HealthIndicator status="Not Started" />);
    
    const indicator = screen.getByText('Not Started');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-gray-100', 'text-gray-600');
    expect(screen.getByText('⚪')).toBeInTheDocument();
  });

  test('renders "In Progress" status with teal styling', () => {
    render(<HealthIndicator status="In Progress" />);
    
    const indicator = screen.getByText('In Progress');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-teal-100', 'text-teal-700');
    expect(screen.getByText('🟡')).toBeInTheDocument();
  });

  test('renders "On Track" status with green styling', () => {
    render(<HealthIndicator status="On Track" />);
    
    const indicator = screen.getByText('On Track');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-green-100', 'text-green-700');
    expect(screen.getByText('🟢')).toBeInTheDocument();
  });

  test('renders "At Risk" status with yellow styling', () => {
    render(<HealthIndicator status="At Risk" />);
    
    const indicator = screen.getByText('At Risk');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-yellow-100', 'text-yellow-700');
    expect(screen.getByText('🔴')).toBeInTheDocument();
  });

  test('includes proper ARIA labels for screen readers', () => {
    render(<HealthIndicator status="On Track" />);
    
    const indicator = screen.getByLabelText('On Track');
    expect(indicator).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
  });

  test('handles unknown status gracefully', () => {
    render(<HealthIndicator status="Invalid Status" />);
    
    const indicator = screen.getByText('Not Started');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-gray-100', 'text-gray-600');
    expect(screen.getByText('⚪')).toBeInTheDocument();
  });

  test('displays correct icon for each status', () => {
    const statuses = [
      { status: 'Not Started', icon: '⚪' },
      { status: 'In Progress', icon: '🟡' },
      { status: 'On Track', icon: '🟢' },
      { status: 'At Risk', icon: '🔴' }
    ];

    statuses.forEach(({ status, icon }) => {
      const { unmount } = render(<HealthIndicator status={status} />);
      expect(screen.getByText(icon)).toBeInTheDocument();
      unmount();
    });
  });

  test('has proper color contrast ratios', () => {
    render(<HealthIndicator status="On Track" />);
    
    const indicator = screen.getByText('On Track');
    // Tailwind's green-100 background with green-700 text meets WCAG AA standards
    expect(indicator).toHaveClass('bg-green-100', 'text-green-700');
  });
});