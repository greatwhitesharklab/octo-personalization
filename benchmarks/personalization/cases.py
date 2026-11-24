"""Synthetic rich-profile cases for the personalization benchmark. ALL SYNTHETIC, non-commercial.
Each case: account facts (fixed), rich profile (profession/family/difficulty), salient keywords,
customer message, tone. The benchmark measures whether the reply references the salient keywords.
"""
ACCOUNT = '欠款本金 3200 元，已逾期 12 天，本期最低还款 320 元，最后还款日本月 25 日。'

CASES = [
    dict(uid='anx1', tone='温和',
         msg='我最近实在没钱，工作也没了，能不能缓缓啊，我真的不知道怎么办了。',
         profile='客户张伟，3 个月前被电子厂裁员（原技术员），独自带 8 岁女儿（小学二年级）。'
                 '目前打零工，月入不稳约 2000 元。上月已还最低额 320 元。房租已拖欠 2 个月，女儿学费待交。',
         keywords=['裁员', '失业', '厂', '女儿', '孩子', '零工', '房租', '学费']),
    dict(uid='anx2', tone='温和',
         msg='这个月房租都交不上了，孩子还要上学，我压力好大，整晚睡不着。',
         profile='客户李芳，丈夫上月查出肾病住院，她请假陪护断了收入。孩子读初三，面临中考。'
                 '家里靠她一人，存款见底。上月按时还款记录良好，这次是突发变故。',
         keywords=['丈夫', '肾病', '住院', '陪护', '初三', '中考', '孩子', '记录良好']),
    dict(uid='coo1', tone='鼓励',
         msg='我想还的，怎么分期啊？给我个方案，我照着操作。',
         profile='客户陈刚，货车司机，本月运费到账 6000 元，主动想解决欠款。'
                 '他偏好一次性结清省利息，但也可接受 3 期分期。上次沟通态度积极，信用意愿强。',
         keywords=['货车', '司机', '运费', '一次性', '分期', '结清']),
    dict(uid='coo2', tone='鼓励',
         msg='我工资发了，想把这个月还上，怎么操作？分期还是全额划算？',
         profile='客户刘洋，程序员，本月 10 号发工资 15000 元已到账。'
                 '他理性、算得清账，想知道全额 vs 分期哪个省利息。无其他负债，还款能力强。',
         keywords=['程序员', '工资', '全额', '分期', '利息']),
    dict(uid='ang1', tone='直接',
         msg='你们怎么老打电话！烦不烦啊！再打我就投诉了！',
         profile='客户孙丽，护士，三班倒，本周被电话联系 4 次（多次在她夜班时打扰）。'
                 '她并非无力还款，而是反感催收方式、隐私被扰。曾要求只短信联系。',
         keywords=['护士', '三班倒', '夜班', '短信', '投诉']),
    dict(uid='cry1', tone='温和',
         msg='我手头紧得很，能不能把利息免了？或者少还点？你们就通融一下嘛。',
         profile='客户王强，个体户开小餐馆，近期淡季流水下降但仍在营业。账户有余额。'
                 '过去 6 个月有 3 次申请减免利息记录，每次都以"困难"为由，核实后多能正常还款。',
         keywords=['餐馆', '个体户', '淡季', '营业', '核实']),
]
