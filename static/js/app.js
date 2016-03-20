(function () {
    angular.module('yals', [])
        .controller('yals_controller', ['$scope', '$http', function ($scope, $http) {
            $scope.pairs = [];
            $scope.notification = "";
            $scope.addLearnData = function () {
                //USE HTML5 reader
                var f = document.getElementById('learning_data').files[0],
                    r = new FileReader();
                r.onloadend = function (e) {
                    var learnData = e.target.result;
                    $http.post('/add_learn', {learn_data: learnData}).success(
                        function (response) {

                        })
                };
                r.readAsBinaryString(f);

            };
            $scope.checkTestData = function () {
                var f = document.getElementById('testing_data').files[0],
                    r = new FileReader();
                r.onloadend = function (e) {
                    var testData = e.target.result;
                    $http.post('/check_test', {testDara: testData}).success(
                        function (response) {
                            $scope.pairs = response.pairs;
                        });
                };
                r.readAsBinaryString(f);
            };
            $scope.dropDb = function () {
                $http.delete('/drop_db', {}).success(
                    function (response) {

                    });
            };
        }]);
}());