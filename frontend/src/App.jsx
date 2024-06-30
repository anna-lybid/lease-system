import { useState, useEffect } from 'react';

function App() {
    const [data, setData] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                // Replace with the specific endpoint you want to fetch from
                const response = await fetch(`${import.meta.env.VITE_API_URL}goals/`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const jsonData = await response.json();
                setData(jsonData);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        fetchData();
    }, []);

    return (
        <>
            <div>
                {/* Render fetched data */}
                {data && (
                    <div>
                        <h2>Goals</h2>
                        <ul>
                            {data.map(goal => (
                                <li key={goal.id}>{goal.name}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </>
    );
}

export default App;
