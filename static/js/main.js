import React from 'react';
import { createRoot } from 'react-dom/client';
import PortfolioChart from './components/PortfolioChart';
import { Info } from 'lucide-react';

document.addEventListener('DOMContentLoaded', function () {
    // Portfolio Chart Initialization
    const chartContainer = document.getElementById('portfolio-chart');
    if (chartContainer) {
        const root = createRoot(chartContainer);
        root.render(React.createElement(PortfolioChart));
    }

    // Toggle functionality for filled orders
    const toggleButton = document.getElementById('toggle-filled-orders');
    const filledOrdersContainer = document.getElementById('filled-orders-container');

    if (toggleButton && filledOrdersContainer) {
        toggleButton.addEventListener('click', function () {
            const isHidden = filledOrdersContainer.style.display === 'none' || !filledOrdersContainer.style.display;
            filledOrdersContainer.style.display = isHidden ? 'block' : 'none';
            toggleButton.textContent = isHidden ? 'Hide Filled Orders' : 'Show Filled Orders';
        });
    }

    // Date simulation form handling
    const dateForm = document.getElementById('simulation-date-form');
    if (dateForm) {
        const dateInput = document.getElementById('sim_date');
        if (dateInput) {
            dateInput.value = dateInput.getAttribute('value');
        }
    }

    // Stock search form handling
    const searchForm = document.getElementById('stock-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            const searchInput = document.getElementById('stock_symbol');
            if (searchInput && !searchInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a stock symbol');
            }
        });
    }

    // Disable Reports and Browse buttons
    const disabledLinks = document.querySelectorAll('a[href="#reports"], a[href="#browse"]');
    disabledLinks.forEach(link => {
        link.classList.add('disabled');
        link.addEventListener('click', (e) => {
            e.preventDefault();
        });
    });

    // Add info button to top bar using React
    const topBar = document.querySelector('.top-bar');
    if (topBar && !document.querySelector('.info-button-container')) {
        const infoButtonContainer = document.createElement('div');
        infoButtonContainer.className = 'info-button-container';
        topBar.insertBefore(infoButtonContainer, topBar.firstChild);

        const root = createRoot(infoButtonContainer);
        root.render(React.createElement('button', {
            className: 'info-button',
            onClick: () => {
                const modal = document.getElementById('project-info-modal');
                if (modal) modal.style.display = "block";
            }
        }, React.createElement(Info, {
            size: 24
        })));

        // Modal functionality
        const modal = document.getElementById('project-info-modal');
        const closeBtn = document.querySelector('.close');

        if (closeBtn) {
            closeBtn.onclick = function () {
                modal.style.display = "none";
            }
        }

        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    }
});