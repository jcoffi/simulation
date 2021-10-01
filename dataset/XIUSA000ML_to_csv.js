const jdata = require('./XIUSA000ML.json')
const fs = require('fs')
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const csvWriter = createCsvWriter({
    path: './XIUSA000ML.csv',
    header: [
        {id: 'i', title: 'Date'},
        {id: 'v', title: 'Close'}
    ]
});

const records = jdata.data.r[0].t[0].d
records.forEach(row => row.v = Number(row.v))

console.log(records)

csvWriter.writeRecords(records)
    .then(() => {
        console.log('...Done');
    });
