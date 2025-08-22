const COLORS = [
    '#4dc9f6',
    '#f67019',
    '#f53794',
    '#537bc4',
    '#acc236',
    '#166a8f',
    '#00a950',
    '#58595b',
    '#8549ba'
];

function getColor(index) {
    return COLORS[index % COLORS.length];
}

fetch('api/lines')
    .then((response) => { return response.json() })
    .then((data) => {
        values = [];
        values = []
        for (let d of data) {
            values.push({ x: d.date * 1000, y: d.value })
        };
        buildChartLines(values);
    })

fetch('api/about')
    .then((response) => { return response.json() })
    .then((data) => {
        document.getElementById('title-branch').innerText = data.branch_name;
        document.getElementById('text-total').innerText = "Total number of comments: " + data['total_number_commit'];
        document.getElementById('text-first').innerText = "Date of the first comment: " + data['date_first_commit'];
        document.getElementById('text-last').innerText = "Date of the last comment: " + data['date_last_commit']
    })

fetch('api/authors')
    .then((response) => { return response.json() })
    .then((data) => {
        labels = [];
        dataValues = [];
        backgroundColor = [];
        let number_author = 0
        for (var d in data) {
            number_author = number_author + 1;
            labels.push(d);
            dataValues.push(data[d].commits);
            backgroundColor.push(getColor(number_author));
        }
        buildChartAuthors(labels, dataValues, backgroundColor);
    })

fetch('api/week')
    .then((response) => { return response.json() })
    .then((data) => {
        let list_authors = new Set();
        for (var key in data) {
            day = data[key];
            for (var author in day) {
                list_authors.add(author);
            }
        }
        let list_days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        let values = [];

        let number_author = 0
        for (let author of list_authors) {
            number_author = number_author + 1;
            dataAuthor = []
            for (var day of list_days_of_week) {
                if (author in data[day]) {
                    dataAuthor.push(data[day][author]);
                } else {
                    dataAuthor.push(0);
                }
            }
            values.push({
                'label': author,
                'data': dataAuthor,
                'backgroundColor': getColor(number_author)
            });
        }
        buildChartWeek(list_days_of_week, values);
    })

fetch('api/day')
    .then((response) => { return response.json() })
    .then((data) => {
        let list_authors = new Set();
        for (var key in data) {
            day = data[key];
            for (var author in day) {
                list_authors.add(author);
            }
        }
        let list_hour_of_day = [];
        for (const d of Array(24).keys()) {
            list_hour_of_day.push(d.toString());
        }
        let values = [];
        let number_author = 0
        for (let author of list_authors) {
            number_author = number_author + 1;
            dataAuthor = []
            for (var hour of list_hour_of_day) {
                if (author in data[hour]) {
                    dataAuthor.push(data[hour][author]);
                } else {
                    dataAuthor.push(0);
                }
            }
            values.push({
                'label': author,
                'data': dataAuthor,
                'backgroundColor': getColor(number_author)
            });
        }
        buildChartDay(list_hour_of_day, values);
    })


fetch('api/month')
    .then((response) => { return response.json() })
    .then((data) => {
        let list_authors = new Set();
        for (var key in data) {
            day = data[key];
            for (var author in day) {
                list_authors.add(author);
            }
        }
        let list_days_of_month = [];
        for (const d of Array(32).keys()) {
            if (d > 0) {
                list_days_of_month.push(d.toString());
            }
        }
        let values = [];
        let number_author = 0
        for (let author of list_authors) {
            number_author = number_author + 1;
            dataAuthor = []
            for (var day of list_days_of_month) {
                if (author in data[day]) {
                    dataAuthor.push(data[day][author]);
                } else {
                    dataAuthor.push(0);
                }
            }
            values.push({
                'label': author,
                'data': dataAuthor,
                'backgroundColor': getColor(number_author)
            });
        }
        buildChartMonth(list_days_of_month, values);
    })

function buildChartLines(values) {
    const ctx = document.getElementById('chartLines');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{ data: values }]
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                    }
                }
            }
        }
    });
}

function buildChartAuthors(labels, dataValues, backgroundColor) {
    const ctx = document.getElementById('chartAuthors');
    const myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [
                {
                    data: dataValues,
                    backgroundColor: backgroundColor
                }
            ]
        },
        options: {}
    });
}

function buildChartWeek(labels, values) {
    const ctx = document.getElementById('chartWeek');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: values
        },
        options: {}
    });
}

function buildChartDay(labels, values) {
    const ctx = document.getElementById('chartDay');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: values
        },
        options: {}
    });
}

function buildChartMonth(labels, values) {
    const ctx = document.getElementById('chartMonth');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: values
        },
        options: {}
    });
}

fetch('api/authors')
    .then((response) => response.json())
    .then((data) => {
        const tableBody = document.getElementById('authorsTableBody');
        for (const author in data) {
            const row = document.createElement('tr');

            const nameCell = document.createElement('td');
            nameCell.textContent = author;
            row.appendChild(nameCell);

            const commitsCell = document.createElement('td');
            commitsCell.textContent = data[author].commits;
            row.appendChild(commitsCell);

            const insertionsCell = document.createElement('td');
            insertionsCell.textContent = data[author].insertions;
            row.appendChild(insertionsCell);

            const deletionsCell = document.createElement('td');
            deletionsCell.textContent = data[author].deletions;
            row.appendChild(deletionsCell);

            tableBody.appendChild(row);
        }
    });

fetch('api/commit_types')
    .then((response) => response.json())
    .then((data) => {
        const labels = Object.keys(data).sort();
        const types = new Set();

        for (const date in data) {
            for (const type in data[date]) {
                types.add(type);
            }
        }

        const datasets = [];
        let colorIndex = 0;

        for (const type of types) {
            const dataValues = labels.map((date) => data[date]?.[type] || 0);
            datasets.push({
                label: type,
                data: dataValues,
                backgroundColor: getColor(colorIndex),
            });
            colorIndex++;
        }

        buildChartTypesComments(labels, datasets);
    });

function buildChartTypesComments(labels, datasets) {
    const ctx = document.getElementById('typesCommits');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
            },
            responsive: true,
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true,
                },
            },
        },
    });
}