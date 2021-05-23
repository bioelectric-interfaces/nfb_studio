Example of the pipeline
=======================

Consider a parietal alpha rhythm training with 5 training sessions along with pauses, as well as baselines before and after the main part.
In the "General" property we give a name to the experiment and choose "Mitsar" inlet since we want to use LSL-stream from another program. At the start of the experiment, there will be a window with signals and raw data, and a separated subject's windows. 

.. image:: generalEx.png
   :width: 600

Since the signal is parietal alpha rhythm, we choose Pz for a spatial filter and 7-13 Hz for a Butterworth filter with the second order and lenght of 1000 samples.

The resulted envelope should be fast-processed and smooth enough, so we choose cFIR envelope detector and exponential smoothing with 0.95 factor.\

Finally, we name derived signal in order to use this nama in the block property.

We don't use artificial delay since we don't study effects of latency of the neurofeedback.
   
.. image:: signalEx.png
   :width: 600
   
.. image:: baseEx.png
   :width: 600

.. image:: pauseEx.png
   :width: 600

.. image:: fbEx.png
   :width: 600


.. image:: groupEx.png
   :width: 600

.. image:: sequenceEx.png
   :width: 600
