import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const PortfolioChart = () => {
    const chartData = window.portfolioHistory?.map(day => ({
        date: new Date(day.date).toLocaleDateString(),
        value: day.portfolio_value,
        pnl: day.total_pnl
    })) || [];

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div style={{
                    backgroundColor: 'white',
                    padding: '10px',
                    border: '1px solid #ccc',
                    borderRadius: '4px'
                }}>
                    <p style={{ margin: '0 0 5px 0' }}>{label}</p>
                    <p style={{ margin: '0', color: '#7db2eb' }}>
                        Value: {formatCurrency(payload[0].value)}
                    </p>
                    <p style={{
                        margin: '0',
                        color: payload[1].value >= 0 ? '#28a745' : '#dc3545'
                    }}>
                        P&L: {formatCurrency(payload[1].value)}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
                <LineChart
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                    />
                    <YAxis
                        tickFormatter={formatCurrency}
                        tick={{ fontSize: 12 }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#7db2eb"
                        strokeWidth={2}
                        dot={false}
                        name="Portfolio Value"
                    />
                    <Line
                        type="monotone"
                        dataKey="pnl"
                        stroke="#82ca9d"
                        strokeWidth={2}
                        dot={false}
                        name="P&L"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PortfolioChart;