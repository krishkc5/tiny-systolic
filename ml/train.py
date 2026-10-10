"""Train/calibrate once; export a reproducible signed-INT4 inference fixture.
Only training data determine parameters/scales. Test labels are evaluation only.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]

def main():
    data=load_digits()
    train,test=train_test_split(np.arange(len(data.target)), test_size=0.2,
                               stratify=data.target,random_state=42)
    x=data.data/16.0; y=data.target
    with threadpool_limits(limits=1):
        model=MLPClassifier(hidden_layer_sizes=(16,),activation="relu",solver="lbfgs",
                            alpha=0.01,max_iter=2000,random_state=42)
        model.fit(x[train],y[train])
    w1,w2=model.coefs_;b1,b2=model.intercepts_
    s1=np.maximum(np.max(np.abs(w1),axis=0)/7,1e-12)
    s2=np.maximum(np.max(np.abs(w2),axis=0)/7,1e-12)
    q1=np.clip(np.rint(w1/s1),-7,7).astype(int)
    q2=np.clip(np.rint(w2/s2),-7,7).astype(int)
    qx=np.clip(np.rint(x*7),0,7).astype(int)
    h=np.maximum((qx@q1)*(s1/7)+b1,0)
    # Calibration uses training examples only; fixed max range, no test tuning.
    hs=max(float(np.max(h[train]))/7,1e-12)
    qh=np.clip(np.rint(h/hs),0,7).astype(int)
    logits=(qh@q2)*(hs*s2)+b2
    predictions=np.argmax(logits[test],axis=1)
    fixture={"seed":42,"train_indices":train.tolist(),"test_indices":test.tolist(),
             "labels":y[test].tolist(),"input_int4":qx[test].tolist(),
             "weights1":q1.tolist(),"weights2":q2.tolist(),
             "scale1":(s1/7).tolist(),"scale2":(hs*s2).tolist(),
             "bias1":b1.tolist(),"bias2":b2.tolist(),"hidden_scale":hs,
             "reference_predictions":predictions.tolist(),
             "reference_hidden":qh[test].tolist()}
    report={"dataset":"sklearn 8x8 handwritten digits","train_samples":len(train),
            "test_samples":len(test),"architecture":[64,16,10],
            "float_correct":int(np.sum(model.predict(x[test])==y[test])),
            "int4_correct":int(np.sum(predictions==y[test])),
            "float_accuracy":float(np.mean(model.predict(x[test])==y[test])),
            "int4_accuracy":float(np.mean(predictions==y[test])),
            "training_iterations":int(model.n_iter_),
            "quantization":"symmetric per-output-channel weights; unsigned 0..7 activations in signed INT4; float host scaling/bias/ReLU",
            "test_split":"stratified 20%, random_state=42; no test-based calibration"}
    (ROOT/'ml/fixtures').mkdir(exist_ok=True)
    (ROOT/'ml/fixtures/digits_int4.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
    (ROOT/'reports/ml-software.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
