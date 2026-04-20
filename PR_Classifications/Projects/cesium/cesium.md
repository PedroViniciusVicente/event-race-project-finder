PR URL: https://github.com/CesiumGS/cesium/pull/8444

## Setup
```
git clone https://github.com/CesiumGS/cesium.git
cd cesium/
git checkout -f 4dcbb1e408c86fb18ce72e98ab6eb390e0b82ae7

nvm use 10
npm install
npm run build

(run all tests)
npx karma start Specs/karma.conf.js --single-run --browsers ChromeCI
// colocar o CI na frente do Chrome para ele abrir a aba do Chrome no background
```


## Reported race condition
go to cesium/Specs/Scene/CameraSpec.js and add the test '_currentFlight is not set for a flight that doesn\'t go anywhere' between the tests 'switches projections' and 'flyTo zooms in between minimumZoomDistance and maximumZoomDistance'
```
fit('_currentFlight is not set for a flight that doesn\'t go anywhere', function() {
    var complete = jasmine.createSpy('complete');
    spyOn(CameraFlightPath, 'createTween').and.returnValue({ complete: complete, duration: 0 });
    spyOn(scene.tweens, 'add');
        
    camera.flyTo({ complete: complete, destination: Cartesian3.fromDegrees(-117.16, 32.71, 5000) });
    //expect(complete).toHaveBeenCalled(); // tweenOptions.complete(); is called when duration == 0 only in the fixed version
    expect(camera._currentFlight).toBeUndefined();
});
```

run just the fit test, skipping the other tests
```
npx karma start Specs/karma.conf.js --single-run --browsers ChromeCI
```

## Surpress the skipped tests, adding the specReporter in Specs/karma.conf.js in line 62
```
reporters : ['spec', 'longest'],
specReporter: {
    suppressSkipped: true,
},
longestSpecsToReport : 10,
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/cesium"
LOG_DIRECTORY = "PRs/pr154/logs_cesium"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'karma', 
    'start', 'Specs/karma.conf.js',
    '--single-run', '--browsers',
    'ChromeCI'
]
# ===================================
```