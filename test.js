var input = [{day: '1', name: 'John'},
{day: '2', name: 'Doe'},
{day: '7', name: '46'},
{day: '1', name: 'Joseph'}];
// var grouped = _.groupBy(person,day);

var output = input.reduce(function(result, value) { 
  result[value.day] = result[value.day] || []; 
  result[value.day].push({name: value.name, day: value.day });
  return result; 
}, {});

console.log(output);

for (i=0; i<10; i++) {
	if (output[i + '']) {
		for (j=0; j<10; j++) {
			if (output[i+''][j]) {
				console.log(output[i + ''][j]['name'].substring(0, 5));
			}
		}
	}
}