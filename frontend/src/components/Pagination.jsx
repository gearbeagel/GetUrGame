import React from 'react';
import NeonButton from './NeonButton';

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  return (
    <div className="flex justify-center items-center space-x-4 mt-8">
      <NeonButton
        color="blue"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Previous
      </NeonButton>
      <span className="text-white">
        Page {currentPage} of {totalPages}
      </span>
      <NeonButton
        color="blue"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </NeonButton>
    </div>
  );
};

export default Pagination;
