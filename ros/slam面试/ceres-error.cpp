#include<ceres/ceres.h>

struct TwoD{
    TwoD(double observed_distance): observed_distance_(observed_distance){}

    template <typename T>
    bool operator()(const T* const p1, const T* const p2, T* residual)const{
        const T dx = p1[0] - p2[0];
        const T dy = p1[1] - p2[1];
        const T predict_distance  = ceres::sqrt(dx * dx + dy * dy);
        residual[0] = predict_distance - observed_distance_;
        return true;
    }

    double observed_distance_;
};

int main(int argc, char** argv){
    google::InitGoogleLogging(argv[0]);

    double m = 0.0;
    double c = 0.0;

    ceres::Problem problem;
    for (int i = 0; i < kNumObservations; ++i){
        problem.AddResidualBlock(
            new ceres::AutoDiffCostFunction<ExponResidual, 1, 2, 2> 
        (new ExponResidual(data[2 * i], data[2 * i + 1])),  // 类型是CostFunction*  
        nullptr,
        &p1,
        &p2); 
    }

    ceres::Solver::Options options;
    options.max_num_iterations = 25;
    options.linear_solver_type = ceres::DENSE_QR;
    options.minimizer_progress_to_stdout = true;

    ceres::Solver::Summary summary;
    ceres::Solve(options, &problem, &summary);
    std::cout << "Final   m: " << m << " c: " << c << "\n";
    return 0;
}