document.addEventListener('DOMContentLoaded', function() {
    const aiArrangeBtn = document.getElementById('ai-arrange-btn');
    const taskList = document.getElementById('task-list');

    if (aiArrangeBtn && taskList) {
        aiArrangeBtn.addEventListener('click', function() {
            fetch('/ai_arrange', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Get all existing task cards
                    const taskCards = taskList.querySelectorAll('.card');

                    // Create a map of task titles to their respective card elements
                    const taskCardMap = new Map();
                    taskCards.forEach(card => {
                        const title = card.querySelector('.card-title').textContent;
                        taskCardMap.set(title, card);
                    });

                    // Clear the existing task list
                    taskList.innerHTML = '';

                    // Separate the completed tasks
                    const completedTasks = data.ordered_tasks.filter(task => task.status.toLowerCase() === 'completed');
                    const nonCompletedTasks = data.ordered_tasks.filter(task => task.status.toLowerCase() !== 'completed');

                    // Append the non-completed tasks first, in the suggested order
                    nonCompletedTasks.forEach(task => {
                        const card = taskCardMap.get(task.title);
                        if (card) {
                            taskList.appendChild(card);
                        } else {
                            console.warn(`Card not found for task: ${task.title}`);
                        }
                    });

                    // Append the completed tasks at the end
                    completedTasks.forEach(task => {
                        const card = taskCardMap.get(task.title);
                        if (card) {
                            taskList.appendChild(card);
                        } else {
                            console.warn(`Card not found for task: ${task.title}`);
                        }
                    });
                } else {
                    console.error('Failed to arrange tasks:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    } else {
        console.error('AI Arrange button or task list not found');
    }
});