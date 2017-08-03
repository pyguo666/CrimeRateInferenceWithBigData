'''
Calculate MAE and MRE use 4 combination.
Generate predicted crimerate.

Yang Guo
'''
from linearRegression import *
from NBRegression import *

def generateMAE_MRE():
    F, Y = generateFeatures(features=['demos', 'geo'])
    mae1_DG, mre1_DG = LRTraining(F, Y)
    mae2_DG, mre2_DG = NBTraining(F, Y)

    F, Y = generateFeatures(features=['demos', 'geo', 'tf'])
    mae1_DGT, mre1_DGT = LRTraining(F, Y)
    mae2_DGT, mre2_DGT = NBTraining(F, Y)

    F, Y = generateFeatures(features=['demos', 'geo', 'poi'])
    mae1_DGP, mre1_DGP = LRTraining(F, Y)
    mae2_DGP, mre2_DGP = NBTraining(F, Y)

    F, Y = generateFeatures()
    mae1_ALL, mre1_ALL = LRTraining(F, Y)
    mae2_ALL, mre2_ALL = NBTraining(F, Y)

    res = [
        [mae1_DG, mae1_DGT, mae1_DGP, mae1_ALL],
        [mre1_DG, mre1_DGT, mre1_DGP, mre1_ALL],
        [mae2_DG, mae2_DGT, mae2_DGP, mae2_ALL],
        [mre2_DG, mre2_DGT, mre2_DGP, mre2_ALL],
    ]

    # print(res)
    outfile = open('result/Performance_evaluation.csv', 'w')
    writer = csv.writer(outfile, delimiter=',', quotechar='"')
    writer.writerows(res)
    outfile.close()

def getPredictedCrimeRate():
    '''
    Calculate and save predicted crime rate by LR and NBR.
    '''
    res = []
    F, Y = generateFeatures()
    for i in range(len(Y)):
        F_train, Y_train = generateFeatures(leaveOut=i+1)

        mod_LR = linearRegression(F_train, Y_train)
        y_predict_LR = mod_LR.predict(F[i,])
        model_NB = sm.GLM(Y_train, F_train, family=sm.families.NegativeBinomial())
        model_res = model_NB.fit()
        y_predict_NBR = model_NB.predict(model_res.params, F[i,])

        res.append([y_predict_LR[0][0], y_predict_NBR])

    outfile = open('result/crimeRate_predict.csv', 'w')
    writer = csv.writer(outfile, delimiter=',', quotechar='"')
    writer.writerows(res)
    outfile.close()



if __name__ == '__main__':
    # generateMAE_MRE()     #generate performance evaluation table.
    getPredictedCrimeRate()
