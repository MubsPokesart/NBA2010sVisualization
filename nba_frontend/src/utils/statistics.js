export const calculateStats = (seasonData) => {
    const west = seasonData.filter(team => team.conference === 'Western');
    const east = seasonData.filter(team => team.conference === 'Eastern');
   
    return [
      {
        diff: mean(west.map(t => t.relative_offensive_rating)) - 
              mean(east.map(t => t.relative_offensive_rating)),
        pValue: tTest(
          west.map(t => t.relative_offensive_rating),
          east.map(t => t.relative_offensive_rating)
        )
      },
      {
        diff: mean(west.map(t => t.relative_defensive_rating)) - 
              mean(east.map(t => t.relative_defensive_rating)),
        pValue: tTest(
          west.map(t => t.relative_defensive_rating),
          east.map(t => t.relative_defensive_rating)
        )
      },
      {
        diff: mean(west.map(t => t.relative_net_rating)) - 
              mean(east.map(t => t.relative_net_rating)),
        pValue: tTest(
          west.map(t => t.relative_net_rating),
          east.map(t => t.relative_net_rating)
        )
      }
    ];
   };
   
const mean = arr => arr.reduce((a, b) => a + b, 0) / arr.length;

const variance = arr => {
    const m = mean(arr);
    return arr.reduce((a, b) => a + Math.pow(b - m, 2), 0) / (arr.length - 1);
};

const tTest = (arr1, arr2) => {
    const n1 = arr1.length;
    const n2 = arr2.length;
    const mean1 = mean(arr1);
    const mean2 = mean(arr2);
    const var1 = variance(arr1);
    const var2 = variance(arr2);

    const t = (mean1 - mean2) / Math.sqrt((var1/n1) + (var2/n2));
    const df = n1 + n2 - 2;

    return tDistribution(Math.abs(t), df);
};

const tDistribution = (t, df) => {
    return 2 * (1 - normalCDF(t));
};

const normalCDF = (x) => {
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989423 * Math.exp(-x * x / 2);
    const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - p : p;
};