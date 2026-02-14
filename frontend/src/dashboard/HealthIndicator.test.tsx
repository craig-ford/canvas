import React from 'react';
import { render, screen } from '@testing-library/react';
import HealthIndicator from '../HealthIndicator';

describe('HealthIndicator', () => {
  test('renders "Not Started" status with correct styling', () => {
    render(<HealthIndicator status="Not Started" />);
    
    const indicator = screen.getByText('Not Started');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-gray-100', 'text-gray-600');
    expect(screen.getByText('⚪')).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
  });

  test('renders "In Progress" status with correct styling', () => {
    render(<HealthIndicator status="In Progress" />);
    
    const indicator = screen.getByText('In Progress');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-teal-100', 'text-teal-700');
    expect(screen.getByText('🟡')).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
  });

  test('renders "On Track" status with correct styling', () => {
    render(<HealthIndicator status="On Track" />);
    
    const indicator = screen.getByText('On Track');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-green-100', 'text-green-700');
    expect(screen.getByText('🟢')).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
  });

  test('renders "At Risk" status with correct styling', () => {
    render(<HealthIndicator status="At Risk" />);
    
    const indicator = screen.getByText('At Risk');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-yellow-100', 'text-yellow-700');
    expect(screen.getByText('🔴')).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
  });

  test('falls back to "Not Started" for invalid status', () => {
    render(<HealthIndicator status="Invalid Status" />);
    
    const indicator = screen.getByText('Not Started');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-gray-100', 'text-gray-600');
    expect(screen.getByText('⚪')).toBeInTheDocument();
  });

  test('has proper accessibility attributes', () => {
    render(<HealthIndicator status="On Track" />);
    
    const indicator = screen.getByLabelText('On Track');
    expect(indicator).toBeInTheDocument();
    
    const screenReaderText = screen.getByText('Health status:');
    expect(screenReaderText).toHaveClass('sr-only');
    
    // Check semantic structure
    expect(indicator.tagName).toBe('SPAN');
  });

  test('applies correct CSS classes for each status', () => {
    const testCases = [
      { status: 'Not Started', bgClass: 'bg-gray-100', textClass: 'text-gray-600' },
      { status: 'In Progress', bgClass: 'bg-teal-100', textClass: 'text-teal-700' },
      { status: 'On Track', bgClass: 'bg-green-100', textClass: 'text-green-700' },
      { status: 'At Risk', bgClass: 'bg-yellow-100', textClass: 'text-yellow-700' }
    ];

    testCases.forEach(({ status, bgClass, textClass }) => {
      const { unmount } = render(<HealthIndicator status={status} />);
      
      const indicator = screen.getByText(status);
      expect(indicator).toHaveClass(bgClass, textClass, 'px-2', 'py-1', 'rounded-full', 'text-xs', 'font-medium');
      
      unmount();
    });
  });
});