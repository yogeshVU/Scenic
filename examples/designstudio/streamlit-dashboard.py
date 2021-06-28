#!/usr/bin/env python
import streamlit as st

import scenic.syntax.translator as translator
import scenic.core.errors as errors
import time

carlafilepath = '/home/ubuntu/yogesh/autonomous/scenic_dev/Scenic/examples/carla/Carla_Challenge'
base_outputdir = "/home/ubuntu/yogesh/output/"
SceneCatalog = dict([('oas_scenario',
                      str('/home/ubuntu/yogesh/autonomous/scenic_dev/Scenic/examples/driving/OAS_Scenarios/oas_scenario_03.scenic')),
                     # ('Carla_Challenge_1',carlafilepath +str('/carlaChallenge1.scenic')) ,
                     # ('Carla_Challenge_2',carlafilepath +str('/carlaChallenge2.scenic') ),
                     # ('Carla_Challenge_3',carlafilepath +str('/carlaChallenge3_static.scenic') ),
                     # ('Carla_Challenge_4',carlafilepath +str('/carlaChallenge4.scenic') ),
                     ('Carla_Challenge_5', carlafilepath + str('/carlaChallenge5.scenic')),
                     ('Carla_Challenge_6', carlafilepath + str('/carlaChallenge6.scenic')),
                     ('Carla_Challenge_7', carlafilepath + str('/carlaChallenge7.scenic'))])

def generateScene(scenario=None):
    if scenario!=None:
        startTime = time.time()
        scene, iterations = errors.callBeginningScenicTrace(
            lambda: scenario.generate()
        )
        totalTime = time.time() - startTime
        print(f'  Generated scene in {iterations} iterations, {totalTime:.4g} seconds.')
        for param, value in scene.params.items():
            print(f'    Parameter "{param}": {value}')
        return scene, iterations
    else:
        None,None


def main():
    print('Hello world!')

    from streamlit.report_thread import get_report_ctx
    ctx = get_report_ctx()
    print(ctx.session_id)


    st.title("Scenic Design Studio")
    # st.text("Hello World")
    total_scenes = st.slider('Number of Scenes to Generate',min_value=1 , max_value=10 , value=4)  # 👈 this is a widget
    # st.write(x, 'squared is', x * x)
    # # st.sidebar.write("write this to the sidebar....")
    # # Add a selectbox to the sidebar:
    # add_selectbox = st.selectbox(
    #     'How would you like to be contacted?',
    #     ('Email', 'Home phone', 'Mobile phone')
    # )
    # print(add_selectbox)

    # scenicFile = '/home/ubuntu/yogesh/autonomous/scenic_dev/Scenic/examples/driving/OAS_Scenarios/oas_scenario_03.scenic'
    # model ='scenic.simulators.newtonian.model'
    # carlafilepath = '/home/ubuntu/yogesh/autonomous/scenic_dev/Scenic/examples/carla/Carla_Challenge'

    add_selectbox = st.selectbox(
        'Select the Scenario to generate.',
        list(SceneCatalog.keys()),
        index=3
    )
    # print(add_selectbox)
    model = 'scenic.simulators.newtonian.model'
    # scenicFile = '/home/ubuntu/yogesh/autonomous/scenic_dev/Scenic/examples/driving/OAS_Scenarios/oas_scenario_03.scenic'
    scenicFile =  SceneCatalog[add_selectbox]
    # And within an expander
    my_expander = st.beta_expander("SCENIC CODE", expanded=True)
    with my_expander:
        try:
            with open(scenicFile) as input:
                st.code(input.read())
        except FileNotFoundError:
            st.error('File not found.')

    # st.write(scenicFile)
    scenario = errors.callBeginningScenicTrace(
        lambda: translator.scenarioFromFile(scenicFile,
                                            model=model
                                            )
    )
    evaluateScenario(scenario,add_selectbox,total_count=total_scenes)
    for i in range(0, total_scenes):
        st.title("Scene "+str(i+1))
        # st.image('/home/ubuntu/yogesh/output/' +str(ctx.session_id)+"/"+add_selectbox+ "_"+ str(i) + ".png")
        st.image(base_outputdir +str(ctx.session_id)+"/"+add_selectbox+ "_"+ str(i) + ".png")


# @st.cache
def evaluateScenario(scenario,add_selectbox,total_count):
    try:
        its = []
        scenes = []
        startTime = time.time()
        while len(its) < total_count:
            scene, iterations = generateScene(scenario)
            scenes.append(scene)
            its.append(iterations)
        totalTime = time.time() - startTime
        count = len(its)
        print(f'Sampled {len(its)} scenes in {totalTime:.2f} seconds.')
        print(f'Average iterations/scene: {sum(its) / count}')
        print(f'Average time/scene: {totalTime / count:.2f} seconds.')

        latest_iteration = st.empty()
        bar = st.progress(0)

        from streamlit.report_thread import get_report_ctx
        ctx = get_report_ctx()
        # print(ctx.session_id)

        import os
        # base_outputdir
        # if not os.path.exists('/home/ubuntu/yogesh/output/' +str(ctx.session_id)):
        #     os.makedirs('/home/ubuntu/yogesh/output/' +str(ctx.session_id))

        if not os.path.exists(base_outputdir +str(ctx.session_id)):
            os.makedirs(base_outputdir+str(ctx.session_id))

        for i in range(0, len(scenes)):
            # Update the progress bar with each iteration.
            latest_iteration.text(f'Generating Scene {i + 1}')
            bar.progress((int)(i + 1)/len(scenes))
            time.sleep(0.1)
            filename =base_outputdir+str(ctx.session_id)+"/"+ add_selectbox + '_' + str(i) + ".png"
            # filename ='/home/ubuntu/yogesh/output/' +str(ctx.session_id)+"/"+ add_selectbox + '_' + str(i) + ".png"
            print('saving ',filename)
            scenes[i].save(zoom=1, fileName=filename)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
