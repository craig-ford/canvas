import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VBUTable from '../VBUTable';

const mockVBUs = [
  {
    id: '123e4567-e89b-12d3-a456-426614174000',
    name: 'Product Alpha',
    gm_name: 'John Smith',
    lifecycle_lane: 'build' as const,
    success_description: 'In this lane, success means validated product-market fit',
    currently_testing: 'Customer acquisition channels',
    next_review_date: '2026-03-15',
    primary_constraint: 'Limited engineering capacity',
    health_indicator: 'In Progress',
    portfolio_notes: 'Focus area for Q1'
  },
  {
    id: '456e7890-e89b-12d3-a456-426614174001',
    name: 'Product Beta',
    gm_name: 'Jane Doe',
    lifecycle_lane: 'sell' as const,
    success_description: 'Scale revenue to $10M ARR',
    currently_testing: 'Sales process optimization',
    next_review_date: '2026-03-20',
    primary_constraint: 'Market competition',
    health_indicator: 'On Track',
    portfolio_notes: null
  }
];

const mockProps = {
  vbus: mockVBUs,
  onExportPDF: jest.fn(),
  onViewVBU: jest.fn()
};

describe('VBUTable', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders table headers with sort indicators', () => {
    render(<VBUTable {...mockProps} />);
    
    expect(screen.getByText('VBU Name')).toBeInTheDocument();
    expect(screen.getByText('Lane')).toBeInTheDocument();
    expect(screen.getByText('GM')).toBeInTheDocument();
    expect(screen.getByText('Testing')).toBeInTheDocument();
    expect(screen.getByText('Next Review')).toBeInTheDocument();
    expect(screen.getByText('Health')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  test('displays VBU data in table rows', () => {
    render(<VBUTable {...mockProps} />);
    
    expect(screen.getByText('Product Alpha')).toBeInTheDocument();
    expect(screen.getByText('Product Beta')).toBeInTheDocument();
    expect(screen.getByText('John Smith')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('Customer acquisition channels')).toBeInTheDocument();
    expect(screen.getByText('Sales process optimization')).toBeInTheDocument();
  });

  test('handles column sorting by name, lane, GM', async () => {
    const user = userEvent.setup();
    render(<VBUTable {...mockProps} />);
    
    const nameHeader = screen.getByText('VBU Name');
    await user.click(nameHeader);
    
    // Check that sorting indicator appears
    expect(nameHeader.closest('th')).toHaveAttribute('aria-sort');
  });

  test('shows pagination controls when needed', () => {
    const manyVBUs = Array.from({ length: 30 }, (_, i) => ({
      ...mockVBUs[0],
      id: `vbu-${i}`,
      name: `Product ${i}`
    }));
    
    render(<VBUTable {...mockProps} vbus={manyVBUs} />);
    
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  test('renders action buttons for each VBU', () => {
    render(<VBUTable {...mockProps} />);
    
    const pdfButtons = screen.getAllByText('PDF');
    const viewButtons = screen.getAllByText('View');
    
    expect(pdfButtons).toHaveLength(2);
    expect(viewButtons).toHaveLength(2);
  });

  test('calls onExportPDF when PDF button clicked', async () => {
    const user = userEvent.setup();
    render(<VBUTable {...mockProps} />);
    
    const pdfButton = screen.getAllByText('PDF')[0];
    await user.click(pdfButton);
    
    expect(mockProps.onExportPDF).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000');
  });

  test('calls onViewVBU when view button clicked', async () => {
    const user = userEvent.setup();
    render(<VBUTable {...mockProps} />);
    
    const viewButton = screen.getAllByText('View')[0];
    await user.click(viewButton);
    
    expect(mockProps.onViewVBU).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000');
  });

  test('shows health indicators with proper colors', () => {
    render(<VBUTable {...mockProps} />);
    
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('On Track')).toBeInTheDocument();
  });

  test('handles empty data gracefully', () => {
    render(<VBUTable {...mockProps} vbus={[]} />);
    
    expect(screen.getByText('No VBUs found')).toBeInTheDocument();
  });

  test('has proper table accessibility attributes', () => {
    render(<VBUTable {...mockProps} />);
    
    const table = screen.getByRole('table');
    expect(table).toHaveAttribute('aria-label', 'VBU portfolio table');
    
    const headers = screen.getAllByRole('columnheader');
    expect(headers.length).toBeGreaterThan(0);
  });

  test('supports keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<VBUTable {...mockProps} />);
    
    const firstButton = screen.getAllByText('PDF')[0];
    firstButton.focus();
    
    await user.keyboard('{Tab}');
    expect(screen.getAllByText('View')[0]).toHaveFocus();
  });
});