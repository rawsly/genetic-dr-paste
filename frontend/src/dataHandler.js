import _ from 'lodash';

const COLORS = {
    'WHITE': 30,
    'SKIN': 35,
    'BABY_PINK': 35,
    'BABY_BLUE': 35,
    'BLUE': 35,
    'GREEN': 35,
    'SILVER': 35,
    'YELLOW': 35,
    'ORANGE': 40,
    'PINK': 40,
    'RED': 40,
    'DARK_BLUE': 40,
    'GRAY': 40,
    'GOLD': 40,
    'PURPLE': 40,
    'BROWN': 40,
    'BLACK': 50
};

const handleData = (excelData, capacity) => {
    const result = [];
    _.map(excelData, row => {
        const colorDuration = COLORS[row.color];
        const sizeDuration = row.size;
        const numberOfJobs = Math.ceil(row.weight / capacity);

        for (let i = 0; i < numberOfJobs; i++) {
            result.push([colorDuration, sizeDuration]);
        }
    });

    return result;
}

export { handleData };