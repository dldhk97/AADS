from .analyzer import lorem_analyzer

def mlload_module():
    print('[SYSTEM][model_task] Start loading module.')

    response = {}
    response['task_type'] = 'load_module'
    
    try:
        lorem_analyzer.load_module()
        print('[SYSTEM][model_task] Load module successful.')
        
        response['success'] = 'True'
        response['message'] = 'KoGPT2 모듈 로드에 성공하였습니다.'

    except Exception as e:
        print('[SYSTEM][model_task] Failed to load module.', e)
        response['success'] = 'False'
        response['message'] = 'KoGPT2 모듈 로드에 실패하였습니다.'

    return response