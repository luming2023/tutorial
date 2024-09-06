#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/container_of.h>
#include <linux/user-return-notifier.h>
#include <linux/delay.h>
#include <linux/kthread.h>
#include <linux/sched.h>
#include <linux/sched/smt.h>

MODULE_LICENSE("GPL");


struct test_user_return {
	struct user_return_notifier urn;
	bool registered;
	int urn_value_changed;
	struct task_struct *worker;
};

static struct test_user_return __percpu *user_return_test;

static void test_user_return_cb(struct user_return_notifier *urn)
{
	struct test_user_return *tur =
		container_of(urn, struct test_user_return, urn);
	unsigned long flags;

	local_irq_save(flags);
	tur->urn_value_changed++;
	local_irq_restore(flags);
	return;
}

static int test_user_return_worker(void *tur)
{
	struct test_user_return *t;
	t = (struct test_user_return *) tur;
	preempt_disable();
	user_return_notifier_register(&t->urn);
	preempt_enable();
	t->registered = true;
	while (!kthread_should_stop()) {
		static int err_rate = 0;

		msleep (1000);
		if (!test_thread_flag(TIF_USER_RETURN_NOTIFY) && (err_rate == 0)) {
			pr_err("TIF_USER_RETURN_NOTIFY is lost");
			err_rate++;
		}
	}
	return 0;
}
static int init_test_user_return(void)
{
	int r = 0;

	/*test static_branch_likely*/
	if (!static_branch_likely(&sched_smt_present))
		pr_info(" -ENODEV ");
	user_return_test = alloc_percpu(struct test_user_return);
	if (!user_return_test) {
		pr_err("failed to allocate percpu test_user_return\n");
		r = -ENOMEM;
		goto exit;
	}
	{
		unsigned int cpu;
		struct task_struct *task;
		struct test_user_return *tur;
		
		for_each_online_cpu(cpu) {
			tur = per_cpu_ptr(user_return_test, cpu);	
			if (!tur->registered) {
				tur->urn.on_user_return = test_user_return_cb;
				task = kthread_create_on_cpu(test_user_return_worker,
					tur, cpu, "test_user_return");
				if (IS_ERR(task)) 
					pr_err("no test_user_return kthread created for cpu %d",cpu);
				else {
					tur->worker = task;
					wake_up_process(task);
				}
			}
		}
	}

exit:
	return r;
}
static void exit_test_user_return(void)
{
	struct test_user_return *tur;
	int i,ret=0;

	for_each_online_cpu(i) {
		tur = per_cpu_ptr(user_return_test, i);
		if (tur->registered) {
			pr_info("[cpu=%d, %d] ", i, tur->urn_value_changed);
			user_return_notifier_unregister(&tur->urn);
			tur->registered = false;
		}
		if (tur->worker) {
			ret = kthread_stop(tur->worker);	
			if (ret) 
				pr_err("can't stop test_user_return kthread for cpu %d", i);
		}
	}
	free_percpu(user_return_test);
	return;
}

module_init(init_test_user_return);
module_exit(exit_test_user_return);
