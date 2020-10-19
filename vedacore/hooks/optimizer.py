from .base_hook import BaseHook
from vedacore.misc import registry


@registry.register_module('hook')
class OptimizerHook(BaseHook):
    def __init__(self, grad_clip=None):
        self.grad_clip = grad_clip

    def clip_grads(self, params):
        params = list(
            filter(lambda p: p.requires_grad and p.grad is not None, params))
        if len(params) > 0:
            return clip_grad.clip_grad_norm_(params, **self.grad_clip)

    def after_train_iter(self, looper):
        optimizer = looper.train_engine.optimizer
        results = looper.cur_train_results
        optimizer.zero_grad()
        results['loss'].backward()
        optimizer.step()
