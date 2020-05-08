from io import StringIO

import numpy as np
import pandas as pd
from pytest import approx

from pharmpy import Model
from pharmpy.methods.frem.models import calculate_parcov_inits, create_model3b
from pharmpy.methods.frem.results import calculate_results, calculate_results_using_bipp


def test_parcov_inits(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_3.mod')
    params = calculate_parcov_inits(model, 2)
    assert params == approx({'OMEGA(3,1)': 0.02560327, 'OMEGA(3,2)': -0.001618381,
                             'OMEGA(4,1)': -0.06764814, 'OMEGA(4,2)': 0.02350935})


def test_create_model3b(testdata):
    model3 = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_3.mod')
    model1b = Model(testdata / 'nonmem' / 'pheno_real.mod')
    model3b = create_model3b(model1b, model3, 2)
    pset = model3b.parameters
    assert pset['OMEGA(3,1)'].init == approx(0.02560327)
    assert pset['THETA(1)'].init == 0.00469555
    assert model3b.name == 'model_3b'


def test_bipp_covariance(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_4.mod')
    res = calculate_results_using_bipp(model, continuous=['APGR', 'WGT'], categorical=[])
    assert res


def test_frem_results_pheno(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno' / 'model_4.mod')
    np.random.seed(39)
    res = calculate_results(model, continuous=['APGR', 'WGT'], categorical=[], samples=10)

    correct = """parameter,covariate,condition,5th,mean,95th
ETA(1),APGR,5th,0.992878,1.170232,1.374516
ETA(1),APGR,95th,0.860692,0.932424,1.003450
ETA(1),WGT,5th,0.884359,0.950191,1.002978
ETA(1),WGT,95th,0.994012,1.117787,1.283830
ETA(2),APGR,5th,0.782424,0.848066,0.947594
ETA(2),APGR,95th,1.025922,1.083065,1.123609
ETA(2),WGT,5th,0.948503,1.009960,1.063028
ETA(2),WGT,95th,0.883742,0.985236,1.114695
"""
    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.covariate_effects, correct)

    correct = """,parameter,observed,5th,95th
1.0,ETA(1),0.974787628525673,0.9593367843894006,0.9854909268072172
1.0,ETA(2),1.0220100211774878,1.012349218441101,1.0339920096220687
2.0,ETA(1),0.9322193602958176,0.8599867286923504,0.980084302377274
2.0,ETA(2),1.0863060524919126,1.0345496255059552,1.1296662646794886
3.0,ETA(1),1.0091536233934566,0.9992556925445459,1.0246784159697295
3.0,ETA(2),0.9872706597459394,0.9811714050402894,0.9957718295067224
4.0,ETA(1),0.9606207522118253,0.9127785604918797,1.0145140572865807
4.0,ETA(2),1.003501058808901,0.9804506068129765,1.036689308205984
5.0,ETA(1),0.974787628525673,0.9593367843894006,0.9854909268072172
5.0,ETA(2),1.0220100211774878,1.012349218441101,1.0339920096220687
6.0,ETA(1),1.010960869697585,0.963661695359141,1.0811631301038673
6.0,ETA(2),0.9641361715262539,0.940505940861195,0.9968957738071667
7.0,ETA(1),0.9944872959330749,0.9363417797502133,1.0776094734893338
7.0,ETA(2),0.9693908394797994,0.9400036119572719,1.0063230911633092
8.0,ETA(1),0.9589034965235579,0.9362900498129827,0.9781834468976713
8.0,ETA(2),1.0275801091641075,1.01521393540937,1.0501977735430987
9.0,ETA(1),0.9493585953571453,0.9066876059677744,0.9777134836646167
9.0,ETA(2),1.055100455328332,1.026123407696415,1.0818677022836836
10.0,ETA(1),0.974787628525673,0.9593367843894006,0.9854909268072172
10.0,ETA(2),1.0220100211774878,1.012349218441101,1.0339920096220687
11.0,ETA(1),0.9589034965235579,0.9362900498129827,0.9781834468976713
11.0,ETA(2),1.0275801091641075,1.01521393540937,1.0501977735430987
12.0,ETA(1),0.9927094986473942,0.9706357376802432,1.021271658617116
12.0,ETA(2),0.9926514136793081,0.9815727629447806,1.0064843535378503
13.0,ETA(1),0.9765333303674195,0.9412604146840132,1.0178835774242787
13.0,ETA(2),0.998061493423796,0.9810501731031469,1.0214684496295618
14.0,ETA(1),0.9510587575256984,0.9230450397961787,0.9758651105921411
14.0,ETA(2),1.0303765269775598,1.0150209885281523,1.0584564233081082
15.0,ETA(1),0.9668129422805504,0.9497251227201009,0.9805080917957982
15.0,ETA(2),1.0247912807632464,1.0138448908082214,1.0420627217494667
16.0,ETA(1),0.9095267118698269,0.8451695579912881,0.9544010447322537
16.0,ETA(2),1.0951989064762164,1.0487951695159132,1.1424218922489593
17.0,ETA(1),1.0026902520717458,0.9499012913647824,1.0793838679578145
17.0,ETA(2),0.9667599353969294,0.9402547046729717,1.0015980653519216
18.0,ETA(1),0.9944872959330749,0.9363417797502133,1.0776094734893338
18.0,ETA(2),0.9693908394797994,0.9400036119572719,1.0063230911633092
19.0,ETA(1),1.1053966073550503,0.9629357379299879,1.3640728806009257
19.0,ETA(2),0.8533835882796981,0.7888476413378454,0.9558799365805954
20.0,ETA(1),0.9845881945267835,0.9558346523685585,1.0195752907117583
20.0,ETA(2),0.9953527778561793,0.9813113934019563,1.013947048813073
21.0,ETA(1),1.0073496078169473,0.9713390508191215,1.0363221658528678
21.0,ETA(2),1.0109602609890682,0.9935309886707921,1.025531122688278
22.0,ETA(1),0.957189310690998,0.9116170970380146,0.9868068430518218
22.0,ETA(2),1.0522369373511546,1.0214576825045978,1.0778432516922152
23.0,ETA(1),1.2458831194124333,1.133088902727925,1.4061397720484834
23.0,ETA(2),0.8590846978787242,0.7687136807373336,0.9187621656508514
24.0,ETA(1),1.2898065460488006,1.1657680364239118,1.4760761709708103
24.0,ETA(2),0.8298833659920394,0.7321287094027014,0.9005711641197409
25.0,ETA(1),1.078488373466804,0.922417441451828,1.3575906454400832
25.0,ETA(2),0.8603696633602557,0.7925727320880631,0.9691487745058911
26.0,ETA(1),1.0986748496525185,0.8901919490329702,1.3168631345820234
26.0,ETA(2),1.0288376555754981,0.9195873281746982,1.1215322945642971
27.0,ETA(1),1.0707971800371383,1.0412360069436044,1.1138643111132231
27.0,ETA(2),0.9459681291986676,0.9161447196967774,0.9690002051900073
28.0,ETA(1),1.0719302408624465,0.8855533280148942,1.2573219319892077
28.0,ETA(2),1.0372600546071509,0.940140395257873,1.1206403039430781
29.0,ETA(1),0.9432781959243836,0.9096801952807857,0.9735715334987318
29.0,ETA(2),1.0331805548571447,1.0143450347567,1.066964883454876
30.0,ETA(1),0.9810711387023736,0.9162696689002403,1.029227428938969
30.0,ETA(2),1.0436929282351648,1.0075035172172253,1.0700425175276125
31.0,ETA(1),0.9493585953571453,0.9066876059677744,0.9777134836646167
31.0,ETA(2),1.055100455328332,1.026123407696415,1.0818677022836836
32.0,ETA(1),1.1077371892512407,0.8917467985674374,1.3373335359678031
32.0,ETA(2),1.0260454142230664,0.9128426881391386,1.121829964544998
33.0,ETA(1),0.9730450473914594,0.9147145201082749,1.0144730873054162
33.0,ETA(2),1.046533194867676,1.0121914524118214,1.070675097966681
34.0,ETA(1),1.0815630311103914,1.0337143626574623,1.1613946378680682
34.0,ETA(2),0.9212942981483625,0.8867050310918108,0.9619356295232057
35.0,ETA(1),1.1248964293826664,1.0609446875739317,1.2057826868647745
35.0,ETA(2),0.9306682547212441,0.87435124540088,0.9634287928104412
36.0,ETA(1),1.03618429556192,1.0061788844921336,1.0865302734726545
36.0,ETA(2),0.9563075276665232,0.9362176525211622,0.98317367391514
37.0,ETA(1),0.9095267118698269,0.8451695579912881,0.9544010447322537
37.0,ETA(2),1.0951989064762164,1.0487951695159132,1.1424218922489593
38.0,ETA(1),0.9415919426929809,0.9005935221401644,0.9697442793982667
38.0,ETA(2),1.0579717659755008,1.0308110124080698,1.0859194547421445
39.0,ETA(1),0.9382284741437185,0.8169821689823062,1.0301006408464066
39.0,ETA(2),1.109353060529306,1.0288821405870672,1.1683620376570127
40.0,ETA(1),1.0571247398166508,0.9632400042527168,1.214127359672088
40.0,ETA(2),0.907071102862022,0.8634123323118756,0.9760771190521302
41.0,ETA(1),0.9991085337343418,0.9697036622662051,1.0214422085629569
41.0,ETA(2),1.0137114501735511,0.9992427860205819,1.0252585890109587
42.0,ETA(1),1.0372807308673064,0.8794285002565119,1.182120154218783
42.0,ETA(2),1.0485972706172273,0.9681988343737646,1.1194533578487307
43.0,ETA(1),1.0963534159335382,0.9492311673467536,1.3619062827355728
43.0,ETA(2),0.8557059542409411,0.7912770836735552,0.96024368082326
44.0,ETA(1),0.974787628525673,0.9593367843894006,0.9854909268072172
44.0,ETA(2),1.0220100211774878,1.012349218441101,1.0339920096220687
45.0,ETA(1),1.0590178953627924,0.92915212738654,1.2816988683078572
45.0,ETA(2),0.8858159125690391,0.827151158033522,0.9771610721775249
46.0,ETA(1),0.9262487332879905,0.8867811237497973,0.9560417056063454
46.0,ETA(2),1.0637378501642383,1.0356599654379044,1.1028015006001572
47.0,ETA(1),1.0203782758399829,0.8763915628240044,1.147686839535794
47.0,ETA(2),1.0543122625829007,0.9818965510848241,1.118860900772268
48.0,ETA(1),0.8963082917194926,0.8430367133091661,0.943172404453226
48.0,ETA(2),1.0753644675509202,1.04128354307973,1.1376235940022434
49.0,ETA(1),0.9415919426929809,0.9005935221401644,0.9697442793982667
49.0,ETA(2),1.0579717659755008,1.0308110124080698,1.0859194547421445
50.0,ETA(1),0.9765333303674195,0.9412604146840132,1.0178835774242787
50.0,ETA(2),0.998061493423796,0.9810501731031469,1.0214684496295618
51.0,ETA(1),0.887386461639495,0.8263395290889299,0.9333620931009626
51.0,ETA(2),1.10416456025005,1.0576381532943824,1.1671172686095912
52.0,ETA(1),0.9355612866877128,0.8959110409372443,0.9725270186492343
52.0,ETA(2),1.0359922135126096,1.0136695371908564,1.0755431165407223
53.0,ETA(1),0.9730450473914594,0.9147145201082749,1.0144730873054162
53.0,ETA(2),1.046533194867676,1.0121914524118214,1.070675097966681
54.0,ETA(1),0.9810711387023736,0.9162696689002403,1.029227428938969
54.0,ETA(2),1.0436929282351648,1.0075035172172253,1.0700425175276125
55.0,ETA(1),1.0295477996858795,0.9565380087517502,1.144716668016071
55.0,ETA(2),0.936440067918556,0.9011653342305795,0.9887216354869703
56.0,ETA(1),0.988117858694446,0.8902729416221501,1.1354357317303099
56.0,ETA(2),0.9492515715913541,0.8999592334004813,1.0122658639339623
57.0,ETA(1),1.0601384919733423,1.0220413645967354,1.1033173989097529
57.0,ETA(2),0.9713027674849692,0.939202930761611,0.990838099029522
58.0,ETA(1),0.9493585953571453,0.9066876059677744,0.9777134836646167
58.0,ETA(2),1.055100455328332,1.026123407696415,1.0818677022836836
59.0,ETA(1),0.9765333303674195,0.9412604146840132,1.0178835774242787
59.0,ETA(2),0.998061493423796,0.9810501731031469,1.0214684496295618
"""

    correct = pd.read_csv(StringIO(correct), index_col=0)
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.individual_effects, correct)

    correct = """parameter,condition,sd_observed,sd_5th,sd_95th
ETA(1),none,0.19836380718266122,0.12625220807235504,0.24116383177640865
ETA(1),APGR,0.1932828383897819,0.08707073037413292,0.227264629387154
ETA(1),WGT,0.19363776172900196,0.12610674817480064,0.23106986571131838
ETA(1),all,0.1851006246151042,0.08319218476142116,0.21063712891152467
ETA(2),none,0.16105092362355455,0.10866666928073866,0.1908609884096776
ETA(2),APGR,0.1468832868065463,0.10666448185507846,0.17792077638605008
ETA(2),WGT,0.16104200315990183,0.10348820432741489,0.1848351655169244
ETA(2),all,0.14572521381314374,0.10000243896199691,0.17321795298354078
"""
    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.unexplained_variability, correct)

    correct = pd.DataFrame({'5th': [1.0, 0.7], 'mean': [6.423729, 1.525424], '95th': [9.0, 3.2],
                            'stdev': [2.237636, 0.704565], 'ref': [6.423729, 1.525424],
                            'categorical': [False, False], 'other': [np.nan, np.nan]},
                           index=['APGR', 'WGT'])
    correct.index.name = 'covariate'
    pd.testing.assert_frame_equal(res.covariate_statistics, correct)


def test_frem_results_pheno_categorical(testdata):
    model = Model(testdata / 'nonmem' / 'frem' / 'pheno_cat' / 'model_4.mod')
    np.random.seed(8978)
    res = calculate_results(model, continuous=['WGT'], categorical=['APGRX'], samples=10)
    correct = """parameter,covariate,condition,5th,mean,95th
ETA(1),WGT,5th,0.8795189896312912,0.9466445932608492,1.0019433736898327
ETA(1),WGT,95th,0.996753409405885,1.1245702765612209,1.2988798347027322
ETA(1),APGRX,other,0.8940140155148761,1.0564628170434618,1.180632821895565
ETA(2),WGT,5th,0.9597747500913076,1.0044780096197885,1.0388367920062975
ETA(2),WGT,95th,0.9256135592505018,0.9934909758805717,1.0869067285073553
ETA(2),APGRX,other,0.8498363889783136,0.9042760019837373,0.9625854858603431
"""
    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.covariate_effects, correct)

    correct = """,parameter,observed,5th,95th
1.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
1.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
2.0,ETA(1),0.9982279801353178,0.9961754974129978,0.9999887376528835
2.0,ETA(2),1.0002362024187312,0.9988561022449322,1.0013625619913815
3.0,ETA(1),0.9982279801353178,0.9961754974129978,0.9999887376528835
3.0,ETA(2),1.0002362024187312,0.9988561022449322,1.0013625619913815
4.0,ETA(1),0.957307754163352,0.9100965543796544,0.9997759097145897
4.0,ETA(2),1.0058268035357498,0.9722517175177672,1.03406715562261
5.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
5.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
6.0,ETA(1),1.1198437615180021,0.8831584813321066,1.1782056733971158
6.0,ETA(2),0.9085975139522281,0.8481065285538487,0.9571519803894389
7.0,ETA(1),1.1043279079656827,0.8604797412043605,1.1760911414487982
7.0,ETA(2),0.9102871721081347,0.847243801684448,0.9516722679921148
8.0,ETA(1),0.9775537764268318,0.9521504164321406,0.9998696274682877
8.0,ETA(2),1.0030276079249114,0.9854604819404225,1.0175826218218802
9.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
9.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
10.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
10.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
11.0,ETA(1),0.9775537764268318,0.9521504164321406,0.9998696274682877
11.0,ETA(2),1.0030276079249114,0.9854604819404225,1.0175826218218802
12.0,ETA(1),0.9843971586548178,0.9666018849775714,0.9999065077397618
12.0,ETA(2),1.0020962749275129,0.9899047926776734,1.0121467614899562
13.0,ETA(1),0.9707579683714311,0.9379179368744708,0.9998355685723741
13.0,ETA(2),1.003959806488996,0.9810369326341086,1.0230478675704417
14.0,ETA(1),0.9707579683714311,0.9379179368744708,0.9998355685723741
14.0,ETA(2),1.003959806488996,0.9810369326341086,1.0230478675704417
15.0,ETA(1),0.9843971586548178,0.9666018849775714,0.9999065077397618
15.0,ETA(2),1.0020962749275129,0.9899047926776734,1.0121467614899562
16.0,ETA(1),0.9775537764268318,0.9521504164321406,0.9998696274682877
16.0,ETA(2),1.0030276079249114,0.9854604819404225,1.0175826218218802
17.0,ETA(1),1.1120587747082418,0.8717393971542922,1.1771438412043316
17.0,ETA(2),0.9094419506268969,0.847670510557867,0.9544046104963776
18.0,ETA(1),1.1043279079656827,0.8604797412043605,1.1760911414487982
18.0,ETA(2),0.9102871721081347,0.847243801684448,0.9516722679921148
19.0,ETA(1),1.1043279079656827,0.8604797412043605,1.1760911414487982
19.0,ETA(2),0.9102871721081347,0.847243801684448,0.9516722679921148
20.0,ETA(1),0.9775537764268318,0.9521504164321406,0.9998696274682877
20.0,ETA(2),1.0030276079249114,0.9854604819404225,1.0175826218218802
21.0,ETA(1),1.0193394208626636,1.000133275833925,1.0422654425227507
21.0,ETA(2),0.9974525653375061,0.9854027067045796,1.0124413143382474
22.0,ETA(1),0.9982279801353178,0.9961754974129978,0.9999887376528835
22.0,ETA(2),1.0002362024187312,0.9988561022449322,1.0013625619913815
23.0,ETA(1),1.2785614775943503,1.1003289937194964,1.3351992442581495
23.0,ETA(2),0.8927013652341582,0.8073457389553856,1.0156516891799532
24.0,ETA(1),1.2875120694739488,1.1037637764672934,1.3475012626771514
24.0,ETA(2),0.8918724725579285,0.8038964780748514,1.0191753869616802
25.0,ETA(1),1.081456278854311,0.8276338767462144,1.17298756350556
25.0,ETA(2),0.9128275526885249,0.8460194451466414,0.9436645163308721
26.0,ETA(1),1.1476873977211168,1.0014344210976156,1.347458231477817
26.0,ETA(2),0.9818243185728661,0.8996795509244879,1.0931417959688983
27.0,ETA(1),1.1758861925567694,0.9677626703618725,1.1997237544963153
27.0,ETA(2),0.9027083706870129,0.8472287663206124,0.9768111203821574
28.0,ETA(1),1.1239177543868035,1.0011450858153383,1.2876683605687993
28.0,ETA(2),0.9845643411818642,0.9142422749243482,1.0784285287879618
29.0,ETA(1),0.9640094037600635,0.9239010856757123,0.9998043297517443
29.0,ETA(2),1.0048928714242114,0.9766340444350925,1.028542658593207
30.0,ETA(1),1.0193394208626636,1.000133275833925,1.0422654425227507
30.0,ETA(2),0.9974525653375061,0.9854027067045796,1.0124413143382474
31.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
31.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
32.0,ETA(1),1.15572180332646,1.0015365714709226,1.368007341447655
32.0,ETA(2),0.9809126732918086,0.8948773767910769,1.098092493210153
33.0,ETA(1),1.0122531252393103,1.0000822688835964,1.0266667345994933
33.0,ETA(2),0.9983795825420214,0.9906940075302106,1.0078916739823391
34.0,ETA(1),1.1595938501918188,0.9427307320487157,1.1862872831170095
34.0,ETA(2),0.9043870771962372,0.8486762095732241,0.9711170597379941
35.0,ETA(1),1.2261495780850629,1.037012429285081,1.2642718801060513
35.0,ETA(2),0.897690923937966,0.8283850458459037,0.9948641106186222
36.0,ETA(1),1.1435272443151587,0.918396513043013,1.1828209217800907
36.0,ETA(2),0.9060689054839179,0.8488377892537526,0.9654850576952785
37.0,ETA(1),0.9775537764268318,0.9521504164321406,0.9998696274682877
37.0,ETA(2),1.0030276079249114,0.9854604819404225,1.0175826218218802
38.0,ETA(1),0.9843971586548178,0.9666018849775714,0.9999065077397618
38.0,ETA(2),1.0020962749275129,0.9899047926776734,1.0121467614899562
39.0,ETA(1),1.026475324221878,1.0001871121397181,1.05810444634791
39.0,ETA(2),0.9965264088886718,0.9801398502560631,1.0170123286685455
40.0,ETA(1),1.1120587747082418,0.8717393971542922,1.1771438412043316
40.0,ETA(2),0.9094419506268969,0.847670510557867,0.9544046104963776
41.0,ETA(1),1.0122531252393103,1.0000822688835964,1.0266667345994933
41.0,ETA(2),0.9983795825420214,0.9906940075302106,1.0078916739823391
42.0,ETA(1),1.0929889139324802,1.0007991870656014,1.2121075110461517
42.0,ETA(2),0.9882296032263663,0.9340290254804097,1.0591305993512188
43.0,ETA(1),1.0966507850556892,0.8493771486447774,1.175047546742705
43.0,ETA(2),0.9111331791253289,0.8468263934164564,0.9489548731865993
44.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
44.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
45.0,ETA(1),1.0890270323591535,0.8384292912343365,1.1740130298139193
45.0,ETA(2),0.9119799724085443,0.8464182773404689,0.9462523468128368
46.0,ETA(1),0.9707579683714311,0.9379179368744708,0.9998355685723741
46.0,ETA(2),1.003959806488996,0.9810369326341086,1.0230478675704417
47.0,ETA(1),1.0778451443231407,1.0006433035284854,1.1760283298005443
47.0,ETA(2),0.9900673478639636,0.9440834778450923,1.0496166920086503
48.0,ETA(1),0.9440438976964787,0.8831114736366117,0.9997275208657717
48.0,ETA(2),1.007697272512306,0.9635483507007913,1.045205915034314
49.0,ETA(1),0.9843971586548178,0.9666018849775714,0.9999065077397618
49.0,ETA(2),1.0020962749275129,0.9899047926776734,1.0121467614899562
50.0,ETA(1),0.9707579683714311,0.9379179368744708,0.9998355685723741
50.0,ETA(2),1.003959806488996,0.9810369326341086,1.0230478675704417
51.0,ETA(1),0.957307754163352,0.9100965543796544,0.9997759097145897
51.0,ETA(2),1.0058268035357498,0.9722517175177672,1.03406715562261
52.0,ETA(1),0.957307754163352,0.9100965543796544,0.9997759097145897
52.0,ETA(2),1.0058268035357498,0.9722517175177672,1.03406715562261
53.0,ETA(1),1.0122531252393103,1.0000822688835964,1.0266667345994933
53.0,ETA(2),0.9983795825420214,0.9906940075302106,1.0078916739823391
54.0,ETA(1),1.0193394208626636,1.000133275833925,1.0422654425227507
54.0,ETA(2),0.9974525653375061,0.9854027067045796,1.0124413143382474
55.0,ETA(1),1.1120587747082418,0.8717393971542922,1.1771438412043316
55.0,ETA(2),0.9094419506268969,0.847670510557867,0.9544046104963776
56.0,ETA(1),1.073938156098686,0.8169886483954345,1.171971120775575
56.0,ETA(2),0.9136759206966932,0.8456298886285745,0.9426282539602353
57.0,ETA(1),1.0408973456983028,1.0003032782652648,1.090518400457308
57.0,ETA(2),0.9946766750618667,0.969698855863204,1.0262188952974651
58.0,ETA(1),0.9912884480992122,0.9812757561438034,0.9999462106955487
58.0,ETA(2),1.0011658066931033,0.9943699656700683,1.0067401275871808
59.0,ETA(1),0.9707579683714311,0.9379179368744708,0.9998355685723741
59.0,ETA(2),1.003959806488996,0.9810369326341086,1.0230478675704417
"""

    correct = pd.read_csv(StringIO(correct), index_col=0)
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.individual_effects, correct)

    correct = """parameter,condition,sd_observed,sd_5th,sd_95th
ETA(1),none,0.18764141333937986,0.13638146999772185,0.18484526745358448
ETA(1),WGT,0.18248555852725476,0.12090283361468239,0.17725513485455732
ETA(1),APGRX,0.17859851761700796,0.12837093642691694,0.1839726626034972
ETA(1),all,0.17186720148456744,0.11133452984528043,0.1743825267272733
ETA(2),none,0.15093077883586237,0.12132559775383217,0.19972092832303162
ETA(2),WGT,0.15090452947915595,0.11929594842953012,0.19855084412113239
ETA(2),APGRX,0.14429826722004974,0.11513030229148667,0.1861126783736316
ETA(2),all,0.1441532460182698,0.11380319105403863,0.18470095021420732
"""

    correct = pd.read_csv(StringIO(correct))
    correct['parameter'] = correct['parameter'].astype(str)
    pd.testing.assert_frame_equal(res.unexplained_variability, correct)

    correct = pd.DataFrame({'5th': [0.7, 0], 'mean': [1.525424, 0.711864], '95th': [3.2, 1],
                            'stdev': [0.704565, 0.456782], 'ref': [1.525424, 1.0],
                            'categorical': [False, True], 'other': [np.nan, 0]},
                           index=['WGT', 'APGRX'])
    correct.index.name = 'covariate'
    pd.testing.assert_frame_equal(res.covariate_statistics, correct)
